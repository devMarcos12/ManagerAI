"""API HTTP opcional. Iniciar com uvicorn managerai.api:create_app --factory."""
from collections import deque
from contextlib import contextmanager
import json
import os
from pathlib import Path
import secrets
from threading import BoundedSemaphore, Lock
import time
from typing import Literal

from fastapi import FastAPI, Query
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from .data_inventory import load_season, team_ids
from .data_loader import DataError, LocalData
from .explanation import OllamaProvider, canonical
from .service import build_service_report, coverage, render_service_markdown
from .service_schema import ServiceError, ServiceRequest, SERVICE_VERSION
from .ui_support import available_catalog
from .v3_schema import VALIDATED_RECUTS
from .coach_service import TeamRequest, coach_catalog, team_preview, analyze_team
from .http_schema import (AnalysisBody, ReportBody, ErrorBody, HealthBody, CapabilitiesBody,
                          CatalogBody, TeamBody, MatchBody, CoverageBody, display_projection,
                          TeamAnalysisBody, TeamPreviewBody, TeamReportBody, CoachCatalogBody)


def create_app(*, data_root=None, provider=None, cors_origins=None):
    root = Path(data_root or os.environ.get("MANAGERAI_DATA_ROOT", "open-data/data")).resolve()
    if provider is None and os.environ.get("MANAGERAI_OLLAMA_MODEL"):
        provider = OllamaProvider(os.environ["MANAGERAI_OLLAMA_MODEL"], expected_digest=os.environ.get("MANAGERAI_OLLAMA_DIGEST"))
    origins = cors_origins if cors_origins is not None else [x for x in os.environ.get("MANAGERAI_CORS_ORIGINS", "").split(",") if x]
    if "*" in origins:
        raise ValueError("Configure origens CORS explícitas.")
    app = FastAPI(title="ManagerAI Core", version=SERVICE_VERSION,
                  description="Análise histórica e planos condicionais. Sem validação de eficácia esportiva.",
                  responses={code: {"model": ErrorBody} for code in (404, 413, 422, 429, 500, 503)})
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"],
                       allow_headers=["Content-Type"], allow_credentials=False)
    analysis_lock, store_lock = BoundedSemaphore(1), Lock()
    reports, recent = {}, deque()
    ttl, max_bytes = 300, 32_000_000

    def error(code, message, status):
        return JSONResponse({"code": code, "message": message}, status_code=status)

    @app.exception_handler(ServiceError)
    async def service_error(_, exc):
        return error(exc.code, str(exc), exc.status)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_, exc):
        for item in exc.errors():
            original = item.get("ctx", {}).get("error")
            if isinstance(original, ServiceError):
                return error(original.code, str(original), original.status)
        return error("INVALID_REQUEST", "Requisição inválida; consulte o contrato OpenAPI.", 422)

    @app.exception_handler(DataError)
    async def data_error(_, exc):
        return error("DATA_UNAVAILABLE_OR_INVALID", "Dados indisponíveis ou incompatíveis com a análise solicitada.", 422)

    @app.exception_handler(ValueError)
    async def value_error(_, exc):
        return error("INVALID_REQUEST", "IDs, referência temporal ou contexto inválidos.", 422)

    @app.exception_handler(Exception)
    async def execution_error(_, exc):
        return error("EXECUTION_FAILED", "Falha na execução da análise.", 500)

    @app.middleware("http")
    async def bounded_body(request, call_next):
        if request.method == "POST":
            chunks, size = [], 0
            async for chunk in request.stream():
                size += len(chunk)
                if size > 64000:
                    return error("PAYLOAD_TOO_LARGE", "Limite de entrada: 64.000 bytes.", 413)
                chunks.append(chunk)
            request._body = b"".join(chunks)
        return await call_next(request)

    @app.get("/v1/health", response_model=HealthBody, response_model_exclude_unset=True)
    def health():
        return {"status": "ok", "service_version": SERVICE_VERSION,
                "data_present": (root / "competitions.json").is_file()}

    @app.get("/v1/capabilities", response_model=CapabilitiesBody, response_model_exclude_unset=True)
    def capabilities():
        return {"schema_version": SERVICE_VERSION, "engines": ["deterministic"],
                "llm": {"configured": provider is not None, "provider": provider.provider_id if provider else None,
                        "model": provider.model if provider else None, "mode": "validated_claim_selection",
                        "availability": "checked_on_generation"},
                "fine_tuned_model": "experimental_not_promoted", "shots_prediction": "experimental_not_integrated",
                "individual_recommendations": False, "v3_recuts": sorted(VALIDATED_RECUTS),
                "limits": {"request_bytes": 64000, "window": 20, "concurrent_analyses": 1,
                           "analyses_per_minute": 10, "report_bytes": max_bytes,
                           "retained_reports": 8, "report_ttl_seconds": ttl},
                "storage": "Memória por processo; token de acesso por posse; reinício remove relatórios.",
                "data_policies": ["legacy", "quality_v1"]}

    @app.get("/v1/catalog", response_model=list[CatalogBody], response_model_exclude_unset=True)
    def catalog():
        return [{**c, "v3_certified": (c["competition_id"], c["season_id"]) in VALIDATED_RECUTS}
                for c in available_catalog(root)]

    @app.get("/v1/teams", response_model=list[TeamBody], response_model_exclude_unset=True)
    def teams(competition_id: int = Query(gt=0), season_id: int = Query(gt=0)):
        season = load_season(LocalData(root), competition_id, season_id)
        return [{"team_id": tid, "name": name} for tid, name in sorted(season.teams.items())]

    @app.get("/v1/matches", response_model=list[MatchBody], response_model_exclude_unset=True)
    def matches(competition_id: int = Query(gt=0), season_id: int = Query(gt=0)):
        season = load_season(LocalData(root), competition_id, season_id)
        return [{"match_id": m["match_id"], "date": m["match_date"], "home_team_id": team_ids(m)[0],
                 "away_team_id": team_ids(m)[1]} for m in season.matches]

    @app.post("/v1/coverage", response_model=CoverageBody)
    def preview(body: AnalysisBody):
        return coverage(root, ServiceRequest.from_dict(body.model_dump()))

    @contextmanager
    def analysis_slot():
        if not analysis_lock.acquire(blocking=False):
            raise ServiceError("BUSY", "Análise em execução; tente novamente mais tarde.", 429)
        try:
            now = time.monotonic()
            while recent and recent[0] < now - 60:
                recent.popleft()
            if len(recent) >= 10:
                raise ServiceError("RATE_LIMIT", "Limite de análises por minuto atingido.", 429)
            recent.append(now)
            yield now
        finally:
            analysis_lock.release()

    @app.get("/v1/coach/teams", response_model=CoachCatalogBody)
    def coach_teams():
        return coach_catalog(root)

    @app.post("/v1/team-coverage", response_model=TeamPreviewBody)
    def own_preview(body: TeamAnalysisBody):
        return team_preview(root, TeamRequest(**body.model_dump()))

    @app.post("/v1/team-analyses", response_model=TeamReportBody)
    def own_analysis(body: TeamAnalysisBody):
        with analysis_slot():
            result = analyze_team(root, TeamRequest(**body.model_dump()))
            if len(canonical(result).encode()) > max_bytes:
                raise ServiceError("REPORT_TOO_LARGE", "Relatório excede 32 MB; reduza a janela.", 413)
            return result

    @app.post("/v1/analyses", response_model=ReportBody, response_model_exclude_unset=True)
    def analyses(body: AnalysisBody):
        request = ServiceRequest.from_dict(body.model_dump())
        with analysis_slot() as now:
            result = build_service_report(root, request, provider=provider)
            result["request"] = body.model_dump()
            result["display"] = display_projection(result)
            key = secrets.token_urlsafe(32)
            result["report_key"] = key
            payload = canonical(result).encode()
            if len(payload) > max_bytes:
                raise ServiceError("REPORT_TOO_LARGE", "Relatório excede 32 MB; reduza a janela.", 413)
            with store_lock:
                for old in [k for k, (created, _) in reports.items() if created < now - ttl]:
                    del reports[old]
                while len(reports) >= 8:
                    del reports[next(iter(reports))]
                reports[key] = (time.monotonic(), payload)
            return result

    @app.get("/v1/reports/{report_key}", response_model=ReportBody, response_model_exclude_unset=True)
    def report(report_key: str):
        with store_lock:
            item = reports.get(report_key)
            if item is None or item[0] < time.monotonic() - ttl:
                reports.pop(report_key, None)
                raise ServiceError("REPORT_NOT_FOUND", "Relatório ausente ou expirado.", 404)
            return json.loads(item[1])

    @app.get("/v1/reports/{report_key}/export")
    def export(report_key: str, format: Literal["json", "markdown"] = "json"):
        result = report(report_key)
        content = canonical(result) if format == "json" else render_service_markdown(result)
        return Response(content, media_type="application/json" if format == "json" else "text/markdown",
                        headers={"Content-Disposition": f'attachment; filename="managerai.{"json" if format == "json" else "md"}"'})

    return app
