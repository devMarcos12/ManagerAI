"""Matriz de calendários e diagnósticos isolados para certificação futura V3.

Nenhuma função deste módulo acrescenta recortes à allowlist. A matriz não lê
eventos; os diagnósticos de orientação recebem eventos explicitamente fornecidos.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
from statistics import median
from typing import Any, Iterable, Sequence

from .data_inventory import inventory, load_season, team_ids
from .data_loader import DataError, LocalData
from .feature_engineering import METRICS, aggregate, finite, match_features, point
from .statsbomb_provisioning import load_contract, verify_snapshot


PROTOCOL_VERSION = "core-02.1"
CANDIDATES = ((11, 27), (12, 27), (7, 27))


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False,
                      sort_keys=True, separators=(",", ":")).encode("utf-8")


def _domain(entry: dict[str, Any]) -> str:
    gender = {"male": "masculino", "female": "feminino"}.get(entry.get("competition_gender"), "não informado")
    age = "juvenil" if entry.get("competition_youth") is True else "adulto" if entry.get("competition_youth") is False else "idade não informada"
    scope = "seleções" if entry.get("competition_international") is True else "clubes" if entry.get("competition_international") is False else "tipo não informado"
    return f"{gender}; {age}; {scope}"


def _eligible_targets(matches: list[dict[str, Any]], window: int) -> int:
    """Conta alvos bilaterais pelo dia inteiro, sem usar placar ou arquivos."""
    dates: dict[int, list[str]] = defaultdict(list)
    for match in matches:
        for team in team_ids(match):
            dates[team].append(match["match_date"])
    return sum(all(sum(day < match["match_date"] for day in dates[team]) >= window
                   for team in team_ids(match)) for match in matches)


def build_coverage_matrix(data: LocalData, *, audit_date: str,
                          contract: dict[str, Any] | None = None,
                          verification: dict[str, Any] | None = None) -> dict[str, Any]:
    """Recalcula 80 calendários; conteúdo de eventos permanece não avaliado.

    Um clone incompatível pode produzir uma matriz diagnóstica, mas cada linha
    conserva esse estado e nenhuma delas se torna certificada.
    """
    date.fromisoformat(audit_date)
    spec = load_contract() if contract is None else contract
    check = verify_snapshot(data.root, contract=spec) if verification is None else verification
    summary = inventory(data)
    expected = {(r["competition_id"], r["season_id"]): r for r in spec["coverage"]["seasons"]}
    observed = {(r["competition_id"], r["season_id"]): r for r in summary["seasons"]}
    if expected.keys() != observed.keys():
        raise DataError("Pares competição/temporada divergem do contrato CORE-01.")
    catalog = {(r["competition_id"], r["season_id"]): r for r in data.read("competitions.json")}
    rows: list[dict[str, Any]] = []
    for pair in sorted(expected):
        baseline, present = expected[pair], observed[pair]
        season = load_season(data, *pair)
        matches = season.matches
        counts = sorted(t["matches"] for t in present["teams"])
        versions = sorted({tuple(str((m.get("metadata") or {}).get(key, "ausente"))
                                 for key in ("data_version", "shot_fidelity_version", "xy_fidelity_version"))
                           for m in matches})
        coverage = present["coverage"]
        mismatch = (baseline["matches"] != present["matches"] or
                    baseline["events"] != coverage["events"] or
                    baseline["lineups"] != coverage["lineups"] or
                    baseline["three_sixty"] != coverage["three-sixty"])
        reasons = []
        if check["status"] != "compatível":
            reasons.append("Snapshot local incompatível com o contrato CORE-01.")
        if mismatch:
            reasons.append("Cobertura de arquivos diverge do contrato CORE-01.")
        if coverage["events"] != len(matches) or coverage["lineups"] != len(matches):
            reasons.append("Eventos ou escalações ausentes.")
        h5, h10 = (_eligible_targets(matches, n) for n in (5, 10))
        if not h5:
            reasons.append("Nenhum alvo com H5 bilateral no calendário.")
        previously_allowed = list(pair) in spec.get("v3_certified_recuts", [])
        if previously_allowed:
            reasons.append("Par já permitido na V3 anterior; esta matriz não reavalia nem revoga esse estado.")
        reasons.append("Estrutura dos eventos, taxonomia, geometria, orientação e métricas não auditadas nesta matriz.")
        rows.append({
            "competition_id": pair[0], "season_id": pair[1],
            "competition": season.competition, "season": season.season,
            "domain": _domain(catalog[pair]),
            "first_date": min((m["match_date"] for m in matches), default=None),
            "last_date": max((m["match_date"] for m in matches), default=None),
            "matches": len(matches), "teams": len(season.teams),
            "matches_per_team": {"minimum": counts[0] if counts else None,
                                 "median": median(counts) if counts else None,
                                 "maximum": counts[-1] if counts else None},
            "files": {"events_present": coverage["events"], "events_missing": len(matches)-coverage["events"],
                      "lineups_present": coverage["lineups"], "lineups_missing": len(matches)-coverage["lineups"],
                      "three_sixty_present": coverage["three-sixty"],
                      "related_orphans": None},
            "metadata_versions": [{"data_version": v[0], "shot_fidelity_version": v[1],
                                   "xy_fidelity_version": v[2]} for v in versions],
            "bilateral_targets": {"h5_calendar": h5, "h10_calendar": h10,
                                  "h5_calculable": None, "h10_calculable": None},
            "structural_failures": None, "taxonomy_failures": None,
            "spatial_gaps": None, "orientation_status": "não avaliado",
            "temporal_status": "política de calendário calculada; conteúdo não auditado",
            "existing_v3_allowlist": previously_allowed,
            "status": "reprovado" if mismatch else "inelegível" if h5 == 0 else "inconclusivo",
            "reasons": reasons, "calendar_sha256_expected": baseline["calendar_sha256"],
            "calendar_sha256_observed": data.sources[f"matches/{pair[0]}/{pair[1]}.json"],
        })
        rows[-1]["audit_date"] = audit_date
        rows[-1]["source_revision_claimed"] = spec["source"]["revision"]
        rows[-1]["row_fingerprint"] = sha256(_canonical(rows[-1])).hexdigest()
    body = {"protocol_version": PROTOCOL_VERSION, "audit_date": audit_date,
            "source_revision_claimed": spec["source"]["revision"],
            "candidate_priority": [{"competition_id": c, "season_id": s} for c, s in CANDIDATES],
            "snapshot_status": check["status"],
            "snapshot_issue_codes": sorted({i["code"] for i in check.get("issues", [])}),
            "contract_sha256": sha256(_canonical(spec)).hexdigest(),
            "global_orphan_ids": summary["unreferenced_file_ids"],
            "rows": rows}
    body["fingerprint"] = sha256(_canonical(body)).hexdigest()
    return body


def audit_orientation(games: Iterable[tuple[dict[str, Any], list[dict[str, Any]]]]) -> dict[str, Any]:
    """Diagnóstico conservador por equipe e tempo, sem transformar coordenadas.

    Guarda operacional pré-fixada: por grupo, >=3 chutes válidos e >=10
    movimentos válidos. Chutes com mediana x>=80 e >=60% dos movimentos em x
    crescente sustentam a direção. Mediana x<=40 e <=40% indicam inversão.
    Para a temporada, >=10 partidas completas e todos os quatro grupos de cada
    partida precisam concordar; qualquer mistura impede aprovação.
    """
    groups: dict[tuple[int, int, int], dict[str, Any]] = defaultdict(lambda: {"shots": [], "forward": 0, "moves": 0})
    matches: set[int] = set()
    for match, events in games:
        mid = match["match_id"]
        matches.add(mid)
        teams = set(team_ids(match))
        for event in events:
            if event.get("period") not in (1, 2):
                continue
            team = (event.get("team") or {}).get("id")
            if team not in teams:
                continue
            name = (event.get("type") or {}).get("name")
            start = point(event.get("location"))
            group = groups[(mid, team, event["period"])]
            if name == "Shot" and start is not None:
                group["shots"].append(start[0])
            if name in ("Pass", "Carry"):
                payload = event.get(name.lower())
                if not isinstance(payload, dict) or (name == "Pass" and payload.get("outcome")):
                    continue
                end = point(payload.get("end_location"))
                if start is not None and end is not None and end[0] != start[0]:
                    group["moves"] += 1
                    group["forward"] += end[0] > start[0]
    details = []
    for (mid, team, period), value in sorted(groups.items()):
        shots, moves = value["shots"], value["moves"]
        state = "inconclusivo"
        if len(shots) >= 3 and moves >= 10:
            share = value["forward"] / moves
            if median(shots) >= 80 and share >= .6:
                state = "coerente"
            elif median(shots) <= 40 and share <= .4:
                state = "invertida"
            else:
                state = "mista"
        details.append({"match_id": mid, "team_id": team, "period": period,
                        "shots": len(shots), "movements": moves, "status": state})
    return _orientation_result(details, matches)


def _orientation_result(details: list[dict[str, Any]], matches: set[int]) -> dict[str, Any]:
    states = Counter(d["status"] for d in details)
    counts = Counter(d["match_id"] for d in details)
    complete = all(counts[mid] == 4 for mid in matches)
    status = ("inconclusiva" if len(matches) < 10 or not complete or states["inconclusivo"] else
              "mista" if states["mista"] or (states["coerente"] and states["invertida"]) else
              "invertida" if states["invertida"] else "coerente")
    return {"status": status, "matches": len(matches), "group_counts": dict(sorted(states.items())),
            "groups": sorted(details, key=lambda d: (d["match_id"], d["team_id"], d["period"]))}


def audit_game_taxonomy(match: dict[str, Any], events: list[dict[str, Any]],
                        lineups: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Confronta payloads consumidos com os três leitores existentes.

    Tipos extras são diagnósticos. Lacuna espacial/xG preserva null nas métricas
    atuais; incompatibilidade de tipo usado é falha explícita.
    """
    from .v3_features import V3_METRICS, aggregate_v3, analyze_match_v3
    from .v3_history import historical_participation
    from .v3_pipeline import aggregate_sequences
    from .v3_sequences import sequence_summary

    types: set[tuple[str, str]] = set()
    outcomes: set[tuple[str, str]] = set()
    subtypes: set[tuple[str, str, str]] = set()
    failures: set[str] = set()
    gaps: Counter[str] = Counter()
    for event in events:
        if not isinstance(event, dict):
            failures.add("Evento não é objeto JSON.")
            continue
        type_obj = event.get("type")
        if not isinstance(type_obj, dict) or not isinstance(type_obj.get("name"), str):
            failures.add("Tipo de evento inválido.")
            continue
        name = type_obj["name"]
        types.add((str(type_obj.get("id", "ausente")), name))
        payload = event.get(name.lower().replace(" ", "_"))
        if isinstance(payload, dict):
            subtype = payload.get("type")
            if isinstance(subtype, dict) and isinstance(subtype.get("name"), str):
                subtypes.add((name, str(subtype.get("id", "ausente")), subtype["name"]))
        if event.get("period") not in (1, 2):
            continue
        pressure = event.get("under_pressure")
        if pressure is not None and type(pressure) is not bool:
            failures.add("under_pressure incompatível; exige booleano ou ausência.")
        if name in ("Pass", "Carry", "Shot"):
            payload = event.get(name.lower())
            if not isinstance(payload, dict):
                failures.add(f"{name} sem objeto {name.lower()}.")
                continue
            if name in ("Pass", "Carry"):
                if point(event.get("location")) is None or point(payload.get("end_location")) is None:
                    gaps[f"{name} sem geometria válida"] += 1
            else:
                if point(event.get("location")) is None:
                    gaps["Shot sem geometria válida"] += 1
                xg = payload.get("statsbomb_xg")
                if not finite(xg) or not 0 <= xg <= 1:
                    gaps["Shot sem xG válido"] += 1
            outcome = payload.get("outcome")
            if outcome is not None:
                if not isinstance(outcome, dict) or not isinstance(outcome.get("name"), str):
                    failures.add(f"{name}.outcome incompatível.")
                else:
                    outcomes.add((str(outcome.get("id", "ausente")), outcome["name"]))
        if name == "Pressure":
            if point(event.get("location")) is None:
                gaps["Pressure sem geometria válida"] += 1
            if event.get("counterpress") is not None and type(event["counterpress"]) is not bool:
                failures.add("Pressure.counterpress incompatível.")
        if name == "Ball Recovery" and event.get("ball_recovery") is not None:
            recovery = event["ball_recovery"]
            if not isinstance(recovery, dict) or (recovery.get("recovery_failure") is not None
                                                  and type(recovery["recovery_failure"]) is not bool):
                failures.add("Ball Recovery.recovery_failure incompatível.")
        if name == "Duel" and event.get("duel") is not None:
            duel = event["duel"]
            if not isinstance(duel, dict) or (duel.get("type") is not None
                                                and not isinstance(duel["type"], dict)):
                failures.add("Duel.type incompatível.")
    result: dict[str, Any] = {"match_id": match["match_id"],
             "types": [{"id": identifier, "name": name} for identifier, name in sorted(types)],
             "subtypes": [{"event": event, "id": identifier, "name": name}
                          for event, identifier, name in sorted(subtypes)],
             "outcomes": [{"id": identifier, "name": name} for identifier, name in sorted(outcomes)],
             "failures": sorted(failures), "gaps": dict(sorted(gaps.items())),
             "legacy_metric_count": len(METRICS), "v3_metric_count": len(V3_METRICS),
             "teams": []}
    if failures:
        return result
    features, quality = match_features(match, events, lineups)
    result["core_quality"] = quality
    for tid in team_ids(match):
        legacy = aggregate(tid, str(tid), [features[tid]], quality)
        v3_row = analyze_match_v3(match, events, tid, features[tid]["minutes"])
        v3 = aggregate_v3(tid, str(tid), [v3_row])
        sequence = sequence_summary(match, events, tid)
        historical = historical_participation(match, events, lineups, tid)
        seq = aggregate_sequences([sequence])
        result["teams"].append({"team_id": tid,
            "legacy_calculable": sorted(k for k, value in legacy.metrics.items() if value.value is not None),
            "v3_calculable": sorted(k for k, value in v3["metrics"].items() if value["value"] is not None),
            "sequence_calculable": sorted(k for k, value in seq.items() if value["value"] is not None),
            "v3_quality": v3_row["quality"], "sequence_quality": sequence["quality"],
            "historical_quality": historical["quality"]})
    return result


def audit_candidate(data: LocalData, competition_id: int, season_id: int, *,
                    audit_date: str, verification: dict[str, Any] | None = None) -> dict[str, Any]:
    """Lê um único candidato integralmente, com uso de memória por partida.

    Diagnostica sem certificar ou mudar a allowlist. O chamador fornece um clone
    comprovado pela CORE-01; o resultado guarda fontes e calculabilidade real.
    """
    from .v3_features import V3_METRICS

    date.fromisoformat(audit_date)
    check = verify_snapshot(data.root) if verification is None else verification
    if check["status"] != "compatível":
        raise DataError("Snapshot incompatível com CORE-01; auditoria real recusada.")
    season = load_season(data, competition_id, season_id)
    ordered = sorted(season.matches, key=lambda m: (m["match_date"], m.get("kick_off") or "", m["match_id"]))
    all_keys = set(METRICS) | set(V3_METRICS) | {"observed_blocks", "entry_block_share", "shot_block_share"}
    by_match: dict[int, dict[int, set[str]]] = {}
    failures: list[dict[str, Any]] = []
    gaps: Counter[str] = Counter()
    types: set[tuple[str, str]] = set()
    subtypes: set[tuple[str, str, str]] = set()
    outcomes: set[tuple[str, str]] = set()
    event_ids: set[str] = set()
    quality_counts: Counter[str] = Counter()
    orientation_groups: list[dict[str, Any]] = []
    bytes_read = 0
    matches_read = 0
    for match in ordered:
        mid = match["match_id"]
        if not data.exists("events", mid) or not data.exists("lineups", mid):
            failures.append({"match_id": mid, "reason": "Evento ou escalação ausente."})
            continue
        events, lineups = data.events(mid), data.lineups(mid)
        matches_read += 1
        bytes_read += (data.root / "events" / f"{mid}.json").stat().st_size
        bytes_read += (data.root / "lineups" / f"{mid}.json").stat().st_size
        for event in events:
            if isinstance(event, dict) and isinstance(event.get("id"), str):
                if event["id"] in event_ids:
                    failures.append({"match_id": mid, "reason": "ID de evento duplicado entre partidas."})
                event_ids.add(event["id"])
        try:
            diagnosis = audit_game_taxonomy(match, events, lineups)
        except (DataError, KeyError, TypeError, ValueError) as exc:
            failures.append({"match_id": mid, "reason": f"Estrutura/funcionalidade: {exc}"})
            continue
        if diagnosis["failures"]:
            failures.extend({"match_id": mid, "reason": reason} for reason in diagnosis["failures"])
            continue
        gaps.update(diagnosis["gaps"])
        quality_counts.update({f"core.{k}": v for k, v in diagnosis["core_quality"].items()})
        for key in ("event_player_not_in_match_lineup", "durations_invalid",
                    "locations_invalid", "movement_end_invalid"):
            if diagnosis["core_quality"].get(key, 0):
                failures.append({"match_id": mid, "reason": f"Qualidade incompatível: {key}="
                                 f"{diagnosis['core_quality'][key]}."})
        for team in diagnosis["teams"]:
            for family in ("v3", "sequence", "historical"):
                quality_counts.update({f"{family}.{k}": v for k, v in team[f"{family}_quality"].items()})
        types.update((item["id"], item["name"]) for item in diagnosis["types"])
        subtypes.update((item["event"], item["id"], item["name"]) for item in diagnosis["subtypes"])
        outcomes.update((item["id"], item["name"]) for item in diagnosis["outcomes"])
        by_match[mid] = {team["team_id"]: (set(team["legacy_calculable"]) |
                         set(team["v3_calculable"]) | set(team["sequence_calculable"]))
                         for team in diagnosis["teams"]}
        orientation_groups.extend(audit_orientation(((match, events),))["groups"])
    target_counts: dict[str, int] = {}
    for window in (5, 10):
        count = 0
        for target in ordered:
            target_date = target["match_date"]
            sides = team_ids(target)
            history = {}
            for tid in sides:
                previous = [m for m in ordered if tid in team_ids(m) and m["match_date"] < target_date]
                history[tid] = previous[-window:]
            if all(len(history[tid]) == window and all(all_keys <= by_match.get(m["match_id"], {}).get(tid, set())
                                                      for m in history[tid]) for tid in sides):
                count += 1
        target_counts[f"h{window}_calculable"] = count
    orientation = _orientation_result(orientation_groups, {m["match_id"] for m in ordered})
    body = {"protocol_version": PROTOCOL_VERSION, "audit_date": audit_date,
            "competition_id": competition_id, "season_id": season_id,
            "competition": season.competition, "season": season.season,
            "source_revision": check.get("source", {}).get("revision"),
            "matches_cataloged": len(ordered), "matches_read": matches_read,
            "matches_diagnosed": len(by_match),
            "event_and_lineup_bytes_read": bytes_read,
            "target_counts": target_counts,
            "structural_or_taxonomy_failures": failures,
            "quality_counts": dict(sorted(quality_counts.items())),
            "spatial_or_xg_gaps": dict(sorted(gaps.items())),
            "observed_types": [{"id": i, "name": n} for i, n in sorted(types)],
            "observed_subtypes": [{"event": e, "id": i, "name": n} for e, i, n in sorted(subtypes)],
            "observed_outcomes": [{"id": i, "name": n} for i, n in sorted(outcomes)],
            "metadata_versions": sorted({tuple(str((m.get("metadata") or {}).get(key, "ausente"))
                                 for key in ("data_version", "shot_fidelity_version", "xy_fidelity_version"))
                                 for m in ordered}),
            "orientation": orientation,
            "status": "reprovado" if failures else "inconclusivo",
            "reason": "A auditoria automática não altera a allowlist; gates temporal, amostra, versões e teste real exigem revisão explícita.",
            "sources": [{"path": p, "sha256": h} for p, h in sorted(data.sources.items())]}
    body["fingerprint"] = sha256(_canonical(body)).hexdigest()
    return body


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera matriz diagnóstica CORE-02 sem ler eventos.")
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit-date", required=True)
    parser.add_argument("--candidate-competition-id", type=int)
    parser.add_argument("--candidate-season-id", type=int)
    args = parser.parse_args(argv)
    try:
        data = LocalData(args.data_root)
        destination = args.output.absolute()
        if destination.exists() or destination.resolve().is_relative_to(data.root):
            raise DataError("Destino existente ou dentro dos dados; escolha arquivo novo fora dos brutos.")
        if (args.candidate_competition_id is None) != (args.candidate_season_id is None):
            raise DataError("Informe os dois IDs do candidato ou nenhum.")
        matrix = (audit_candidate(data, args.candidate_competition_id,
                                  args.candidate_season_id, audit_date=args.audit_date)
                  if args.candidate_competition_id is not None else
                  build_coverage_matrix(data, audit_date=args.audit_date))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(matrix, ensure_ascii=False, allow_nan=False,
                                          sort_keys=True, indent=2) + "\n", encoding="utf-8")
    except (DataError, OSError, ValueError) as exc:
        parser.exit(2, f"CORE-02: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
