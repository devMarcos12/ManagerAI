"""Dataset pré-jogo de chutes: X congelado antes da leitura separada de y."""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date
from hashlib import sha256
import json
import math
from pathlib import Path, PurePosixPath

from ..data_inventory import Season, load_season, team_ids
from ..data_loader import DataError, LocalData
from ..feature_engineering import match_features
from ..report_schema import AnalysisRequest
from ..temporal import select_history

TASK_ID = "pl_home_shots_pre_match"
TASK_VERSION = "4.3-ab.1"
FEATURE_NAMES = ("home_shots_for_mean_5", "away_shots_against_mean_5")
WINDOW = 5


def digest(value) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _validate_sources(sources, *, observed_match=None, forbidden_match=None):
    if not isinstance(sources, tuple) or not sources:
        raise ValueError("Fontes devem ser tupla imutável não vazia.")
    paths = set()
    for item in sources:
        if not isinstance(item, tuple) or len(item) != 2:
            raise ValueError("Fonte exige par caminho/hash imutável.")
        path, value = item
        if (not isinstance(path, str) or not path or PurePosixPath(path).is_absolute()
                or path != PurePosixPath(path).as_posix() or ".." in PurePosixPath(path).parts
                or "\\" in path or path in paths or not isinstance(value, str)
                or len(value) != 64 or any(c not in "0123456789abcdef" for c in value)):
            raise ValueError("Fonte/digest inválido ou duplicado.")
        paths.add(path)
    if observed_match is not None:
        if (f"events/{observed_match}.json" not in paths
                or not paths <= {f"events/{observed_match}.json", f"lineups/{observed_match}.json"}):
            raise ValueError("Fontes não correspondem à observação.")
    if forbidden_match is not None and paths & {f"events/{forbidden_match}.json", f"lineups/{forbidden_match}.json"}:
        raise ValueError("Proveniência de features contém o alvo.")


@dataclass(frozen=True)
class Fixture:
    match_id: int
    match_date: str
    home_team_id: int
    away_team_id: int

    def __post_init__(self):
        for value in (self.match_id, self.home_team_id, self.away_team_id):
            if type(value) is not int or value <= 0:
                raise ValueError("IDs positivos obrigatórios.")
        if self.home_team_id == self.away_team_id or date.fromisoformat(self.match_date).isoformat() != self.match_date:
            raise ValueError("Confronto/data inválidos.")

    def calendar_record(self) -> dict:
        return {"match_id": self.match_id, "match_date": self.match_date,
                "home_team": {"home_team_id": self.home_team_id},
                "away_team": {"away_team_id": self.away_team_id}}


@dataclass(frozen=True)
class HistoricalEvidence:
    match_id: int
    match_date: str
    team_id: int
    shots_for: int
    shots_against: int
    sources: tuple[tuple[str, str], ...]
    quality: tuple[tuple[str, int], ...]

    def __post_init__(self):
        if any(type(v) is not int or v <= 0 for v in (self.match_id, self.team_id)):
            raise ValueError("IDs de evidência inválidos.")
        if date.fromisoformat(self.match_date).isoformat() != self.match_date:
            raise ValueError("Data de evidência inválida.")
        if not isinstance(self.quality, tuple):
            raise ValueError("Proveniência/qualidade devem ser tuplas imutáveis.")
        _validate_sources(self.sources, observed_match=self.match_id)


@dataclass(frozen=True)
class FeatureRow:
    fixture: Fixture
    home_history: tuple[HistoricalEvidence, ...]
    away_history: tuple[HistoricalEvidence, ...]
    values: tuple[float, float]

    def __post_init__(self):
        if not isinstance(self.fixture, Fixture) or not isinstance(self.values, tuple) or len(self.values) != 2:
            raise ValueError("Contrato de features inválido.")
        means = []
        for history, team in ((self.home_history, self.fixture.home_team_id), (self.away_history, self.fixture.away_team_id)):
            if not isinstance(history, tuple) or len(history) != WINDOW or len({r.match_id for r in history}) != WINDOW:
                raise ValueError("Exatamente cinco partidas históricas únicas por equipe.")
            if list(history) != sorted(history, key=lambda r: (r.match_date, r.match_id)):
                raise ValueError("Histórico deve estar ordenado por data/ID.")
            for row in history:
                if (row.team_id != team or row.match_id == self.fixture.match_id
                        or date.fromisoformat(row.match_date) >= date.fromisoformat(self.fixture.match_date)):
                    raise ValueError("Histórico contém alvo, futuro, mesmo dia ou equipe incompatível.")
                if any(type(v) is not int or v < 0 for v in (row.shots_for, row.shots_against)):
                    raise ValueError("Contagens históricas inválidas.")
                if not row.sources or any(p in (f"events/{self.fixture.match_id}.json", f"lineups/{self.fixture.match_id}.json") for p, _ in row.sources):
                    raise ValueError("Proveniência histórica inválida.")
            key = "shots_for" if team == self.fixture.home_team_id else "shots_against"
            means.append(sum(getattr(row, key) for row in history) / WINDOW)
        if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in self.values) or tuple(means) != self.values:
            raise ValueError("Features inconsistentes com a evidência histórica.")

    @property
    def fingerprint(self) -> str:
        return digest(asdict(self))


def build_pre_match_features(fixture: Fixture, home_history: tuple[HistoricalEvidence, ...],
                             away_history: tuple[HistoricalEvidence, ...]) -> FeatureRow:
    """Função pura: não recebe y, eventos, loader ou calendário com placares."""
    return FeatureRow(fixture, home_history, away_history,
                      (sum(r.shots_for for r in home_history) / WINDOW,
                       sum(r.shots_against for r in away_history) / WINDOW))


@dataclass(frozen=True)
class ObservedLabel:
    match_id: int
    home_shots: int
    sources: tuple[tuple[str, str], ...]

    def __post_init__(self):
        if type(self.match_id) is not int or self.match_id <= 0 or type(self.home_shots) is not int or self.home_shots < 0:
            raise ValueError("Alvo observado inválido.")
        _validate_sources(self.sources, observed_match=self.match_id)


@dataclass(frozen=True)
class Example:
    features: FeatureRow
    label: ObservedLabel

    def __post_init__(self):
        if self.features.fixture.match_id != self.label.match_id:
            raise ValueError("Alvo de outra partida.")


@dataclass(frozen=True)
class Exclusion:
    match_id: int
    match_date: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class SupervisedDataset:
    examples: tuple[Example, ...]
    excluded: tuple[Exclusion, ...]
    metadata_sources: tuple[tuple[str, str], ...]
    source_hashes: tuple[tuple[str, str], ...]
    audit: dict

    def to_dict(self) -> dict:
        return {"task_id": TASK_ID, "task_version": TASK_VERSION, "window": WINDOW,
                "feature_names": FEATURE_NAMES, "examples": [asdict(e) for e in self.examples],
                "excluded": [asdict(e) for e in self.excluded], "metadata_sources": self.metadata_sources,
                "source_hashes": self.source_hashes, "audit": self.audit}


@dataclass(frozen=True)
class QuantitativePrediction:
    model_id: str
    match_id: int
    match_date: str
    prediction: float
    feature_fingerprint: str
    feature_sources: tuple[tuple[str, str], ...]
    sufficient: bool = True
    task_id: str = TASK_ID
    task_version: str = TASK_VERSION
    limitations: tuple[str, ...] = ("Previsão retrospectiva de contagem; não avalia estratégia tática ideal.",)

    def __post_init__(self):
        if (not isinstance(self.model_id, str) or not self.model_id.strip() or type(self.match_id) is not int or self.match_id <= 0
                or type(self.prediction) not in (int, float) or not math.isfinite(self.prediction) or self.prediction < 0
                or self.sufficient is not True or not self.feature_sources or not self.limitations):
            raise ValueError("Previsão quantitativa inválida; insuficiência não produz preenchimento.")
        if date.fromisoformat(self.match_date).isoformat() != self.match_date:
            raise ValueError("Data da previsão inválida.")
        if (not isinstance(self.feature_fingerprint, str) or len(self.feature_fingerprint) != 64
                or any(c not in "0123456789abcdef" for c in self.feature_fingerprint)):
            raise ValueError("Fingerprint de features obrigatório.")
        _validate_sources(self.feature_sources, forbidden_match=self.match_id)
        if self.task_id != TASK_ID or self.task_version != TASK_VERSION:
            raise ValueError("Contrato de tarefa incompatível.")
        if not isinstance(self.limitations, tuple) or any(not isinstance(v, str) or not v.strip() for v in self.limitations):
            raise ValueError("Limitações devem ser tupla de textos.")


def _read_observation(data: LocalData, fixture: Fixture):
    """Reutiliza a validação/cálculo legado; Shot id16/nameShot coerentes."""
    events = data.events(fixture.match_id)
    lineups = data.lineups(fixture.match_id) if data.exists("lineups", fixture.match_id) else None
    rows, quality = match_features(fixture.calendar_record(), events, lineups)
    outcomes, types = Counter(), Counter()
    names_by_id = {}
    for event in events:
        typ = event.get("type", {})
        if type(typ.get("id")) is not int or not isinstance(typ.get("name"), str):
            raise DataError("Tipo de evento sem ID/nome verificável.")
        if (typ["id"] == 16) != (typ["name"] == "Shot"):
            raise DataError("Classificação de Shot inconsistente (ID16/nomeShot).")
        if typ["id"] in names_by_id and names_by_id[typ["id"]] != typ["name"]:
            raise DataError("Mesmo ID de tipo com nomes diferentes.")
        names_by_id[typ["id"]] = typ["name"]
        if any(event.get(key) for key in ("cancelled", "canceled", "annulled", "void", "deleted", "disallowed")):
            raise DataError("Evento com marca explícita de cancelamento; sem política validada para corrigi-lo.")
        types[typ["name"]] += 1
        if typ["name"] == "Shot":
            if not isinstance(event.get("shot"), dict):
                raise DataError("Shot sem objeto shot verificável.")
            if event.get("period") in (1, 2):
                outcomes[(event["shot"].get("outcome") or {}).get("name", "<ausente>")] += 1
    selected = [f"events/{fixture.match_id}.json", f"lineups/{fixture.match_id}.json"]
    sources = tuple(sorted((p, data.sources[p]) for p in selected if p in data.sources))
    return rows, quality, sources, {e["id"] for e in events}, names_by_id, types, outcomes


def extract_observed_label(data: LocalData, fixture: Fixture) -> ObservedLabel:
    """Leitura posterior separada; nenhuma referência ao builder de X."""
    rows, _, sources, _, _, _, _ = _read_observation(data, fixture)
    return ObservedLabel(fixture.match_id, rows[fixture.home_team_id]["shots_for"], sources)


def build_dataset(root: str | Path) -> SupervisedDataset:
    """PL2/27 somente. Erros estruturais bloqueiam; ausência gera exclusão explícita.

    Passo1 congela todas as features a partir de janelas passadas. Passo2 audita
    eventos do recorte e extrai y, sem voltar a chamar o builder de features.
    """
    metadata = LocalData(root)
    original = load_season(metadata, 2, 27)
    fixtures = tuple(sorted((Fixture(m["match_id"], m["match_date"], *team_ids(m)) for m in original.matches),
                            key=lambda m: (m.match_date, m.match_id)))
    # Remover placares e todos os outros campos pós-jogo antes da seleção/features.
    season = Season(2, 27, original.competition, original.season,
                    [m.calendar_record() for m in fixtures], original.teams)
    del original
    history_data = LocalData(root)
    cache = {}
    exclusions = []
    pending = []

    def historical(fixture, tid):
        if fixture.match_id not in cache:
            rows, quality, sources, _, _, _, _ = _read_observation(history_data, fixture)
            cache[fixture.match_id] = (rows, quality, sources)
        rows, quality, sources = cache[fixture.match_id]
        return HistoricalEvidence(fixture.match_id, fixture.match_date, tid,
                                  rows[tid]["shots_for"], rows[tid]["shots_against"], sources,
                                  tuple(sorted(quality.items())))

    by_id = {m.match_id: m for m in fixtures}
    for target in fixtures:
        request = AnalysisRequest(2, 27, target.home_team_id, target.away_team_id,
                                  target_match_id=target.match_id, recent_matches_window=WINDOW)
        histories, _ = select_history(season, request)
        reasons = []
        for role, tid in (("home", target.home_team_id), ("away", target.away_team_id)):
            if len(histories[tid]) < WINDOW:
                reasons.append(f"{role}: somente {len(histories[tid])}/5 partidas anteriores no calendário")
            missing = [m["match_id"] for m in histories[tid] if not history_data.exists("events", m["match_id"])]
            if missing:
                reasons.append(f"{role}: eventos históricos ausentes {missing}; sem reposição")
        if reasons:
            exclusions.append(Exclusion(target.match_id, target.match_date, tuple(reasons)))
            continue
        home = tuple(historical(by_id[m["match_id"]], target.home_team_id) for m in histories[target.home_team_id])
        away = tuple(historical(by_id[m["match_id"]], target.away_team_id) for m in histories[target.away_team_id])
        pending.append(build_pre_match_features(target, home, away))

    # X está inteiramente congelado; uma outra instância faz auditoria/labels.
    label_data = LocalData(root)
    labels = {}
    global_ids = set()
    global_types = {}
    total_quality, type_counts, shot_outcomes = Counter(), Counter(), Counter()
    missing_targets = set()
    for target in fixtures:
        if not label_data.exists("events", target.match_id):
            missing_targets.add(target.match_id)
            continue
        rows, quality, sources, event_ids, type_names, types, outcomes = _read_observation(label_data, target)
        if global_ids & event_ids:
            raise DataError("ID de evento repetido entre partidas; treino bloqueado.")
        global_ids.update(event_ids)
        for tid, name in type_names.items():
            if tid in global_types and global_types[tid] != name:
                raise DataError("Classificação de eventos inconsistente entre partidas.")
            global_types[tid] = name
        for path, sha in sources:
            if path in history_data.sources and history_data.sources[path] != sha:
                raise DataError("Fonte mudou entre features e labels; repetir construção.")
        labels[target.match_id] = ObservedLabel(target.match_id, rows[target.home_team_id]["shots_for"], sources)
        total_quality.update(quality)
        type_counts.update(types)
        shot_outcomes.update(outcomes)
    examples = []
    for row in pending:
        if row.fixture.match_id in missing_targets:
            exclusions.append(Exclusion(row.fixture.match_id, row.fixture.match_date, ("eventos do alvo ausentes; label indisponível",)))
        else:
            examples.append(Example(row, labels[row.fixture.match_id]))
    exclusions.sort(key=lambda e: (e.match_date, e.match_id))
    if len(examples) + len(exclusions) != len(fixtures):
        raise DataError("Auditoria de contabilização de exemplos falhou.")
    if len({e.features.fixture.match_id for e in examples}) != len(examples):
        raise DataError("Partida duplicada no dataset.")
    source_hashes = dict(metadata.sources)
    source_hashes.update(history_data.sources)
    source_hashes.update(label_data.sources)
    audit = {"catalogued_matches": len(fixtures), "observed_matches": len(labels), "valid_examples": len(examples),
             "excluded_matches": len(exclusions), "unique_event_ids": len(global_ids),
             "quality": dict(sorted(total_quality.items())), "event_types": dict(sorted(type_counts.items())),
             "shot_outcomes_regulation_both_teams": dict(sorted(shot_outcomes.items())),
             "explicit_cancellation_flags_detected": 0, "cross_match_duplicate_event_ids": 0,
             "feature_build_completed_before_label_reads": True,
             "definition": "Shot ID16/nomeShot nos períodos1/2, inclui todos outcomes e pênaltis regulamentares; exclui prorrogação/disputa. Sem deduplicação silenciosa ou inferência VAR."}
    return SupervisedDataset(tuple(examples), tuple(exclusions), tuple(sorted(metadata.sources.items())),
                             tuple(sorted(source_hashes.items())), audit)
