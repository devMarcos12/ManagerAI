"""Participação e formações históricas; nunca avaliação ou escalação sugerida.

API ``historical_participation(match, events, lineups, team_id)`` retorna um jogo
com ``players`` (lista por nome), ``formations`` (registros Starting XI/Tactical
Shift), qualidade e limites. Apenas períodos 1/2 e eventos da equipe. Associações
de jogadores exigem ID no roster da própria equipe naquela partida; roster
ausente exclui participação não verificável, sem criar jogadores.

``aggregate_history(rows)`` agrega uma equipe, rejeita jogos duplicados e retorna
``players``, ``initial_formations`` (frequência por jogo com Starting XI único),
``formation_changes`` e cobertura. Denominador individual = partidas com ao menos
uma ação selecionada (Pass/Carry/Shot/Pressure); não minutos nem todas as partidas
do elenco. xG soma somente os chutes atribuídos: qualquer chute com xG inválido
torna o total individual None. Ausência de chute numa participação válida é zero.
Não estima habilidade, disponibilidade futura, minutos, titularidade ideal ou
formação vencedora. Chamador garante seleção anterior ao corte.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from .data_inventory import team_ids
from .data_loader import DataError
from .feature_engineering import finite


LIMITATIONS = [
    "Participação histórica conta ações registradas; não mede habilidade nem indica escalação.",
    "O denominador individual são jogos com ações registradas, sem normalização por minutos.",
    "Formações são registros históricos, sem comprovação de posicionamento contínuo ou eficácia.",
    "Disponibilidade de todos os atletas na partida-alvo é desconhecida.",
]


def _id(value: Any) -> Any:
    return value.get("id") if isinstance(value, dict) else None


def historical_participation(match: dict[str, Any], events: list[dict[str, Any]],
                             lineups: list[dict[str, Any]] | None, team_id: int) -> dict[str, Any]:
    """Exploração de um jogo-fonte, sem leitura de arquivos e sem uso do alvo."""
    if team_id not in team_ids(match):
        raise DataError("Equipe histórica incompatível com a partida.")
    quality: Counter[str] = Counter()
    roster = {}
    teams = [x for x in (lineups or []) if isinstance(x, dict) and x.get("team_id") == team_id]
    roster_verified = len(teams) == 1 and isinstance(teams[0].get("lineup"), list)
    if not roster_verified:
        quality["missing_or_invalid_team_roster"] += 1
    else:
        duplicates = set()
        for player in teams[0]["lineup"]:
            if not isinstance(player, dict) or type(player.get("player_id")) is not int or player["player_id"] <= 0:
                quality["invalid_roster_player"] += 1
                continue
            pid = player["player_id"]
            name = player.get("player_name")
            if not isinstance(name, str) or not name.strip():
                quality["invalid_roster_player_name"] += 1
                continue
            if pid in roster:
                duplicates.add(pid)
                quality["duplicate_roster_player"] += 1
            roster[pid] = name
        for pid in duplicates:
            roster.pop(pid, None)
    players: dict[int, dict[str, Any]] = {}
    formations = []
    seen_ids = set()
    for event in events:
        if not isinstance(event, dict):
            quality["invalid_event_object"] += 1
            continue
        if event.get("period") not in (1, 2) or _id(event.get("team")) != team_id:
            continue
        eid = event.get("id")
        if not isinstance(eid, str) or not eid or eid in seen_ids:
            quality["invalid_or_duplicate_event_id"] += 1
            continue
        seen_ids.add(eid)
        type_object = event.get("type")
        typ = type_object.get("name") if isinstance(type_object, dict) else None
        if typ in ("Starting XI", "Tactical Shift"):
            tactics = event.get("tactics")
            formation = tactics.get("formation") if isinstance(tactics, dict) else None
            if type(formation) is int and formation > 0:
                formations.append({"match_id": match["match_id"], "match_date": match["match_date"],
                                   "team_id": team_id, "event_id": eid, "event_type": typ,
                                   "formation": formation, "period": event["period"],
                                   "timestamp": event.get("timestamp")})
            else:
                quality["invalid_formation"] += 1
            continue
        if typ not in ("Pass", "Carry", "Shot", "Pressure"):
            continue
        pid = _id(event.get("player"))
        if type(pid) is not int or pid not in roster:
            quality["unverified_player_actions_excluded"] += 1
            continue
        player = players.setdefault(pid, {
            "player_id": pid, "name": roster[pid], "availability": "desconhecida",
            "match_ids": [match["match_id"]], "event_ids": [], "total_actions": 0,
            "passes": 0, "passes_completed": 0, "carries": 0, "shots": 0,
            "pressures": 0, "xg": 0.0,
        })
        # Missing payload cannot imply completed pass or recorded carry.
        if typ in ("Pass", "Carry") and not isinstance(event.get(typ.lower()), dict):
            quality["invalid_movement_payload"] += 1
            if not player["event_ids"]:
                players.pop(pid)
            continue
        player["event_ids"].append(eid)
        player["total_actions"] += 1
        if typ == "Pass":
            player["passes"] += 1
            player["passes_completed"] += not bool(event["pass"].get("outcome"))
        elif typ == "Carry":
            player["carries"] += 1
        elif typ == "Pressure":
            player["pressures"] += 1
        elif typ == "Shot":
            player["shots"] += 1
            shot = event.get("shot")
            xg = shot.get("statsbomb_xg") if isinstance(shot, dict) else None
            if not finite(xg) or not 0 <= xg <= 1:
                player["xg"] = None
                quality["invalid_player_shot_xg"] += 1
            elif player["xg"] is not None:
                player["xg"] += xg
    return {"match_id": match["match_id"], "match_date": match["match_date"],
            "team_id": team_id, "roster_verified": roster_verified,
            "players": sorted(players.values(), key=lambda p: (p["name"].casefold(), p["player_id"])),
            "formations": formations, "quality": dict(quality), "limitations": list(LIMITATIONS)}


def aggregate_history(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Agrega apenas participações verificadas, sem ranking ou recomendação."""
    if len({r["team_id"] for r in rows}) > 1:
        raise DataError("Histórico não pode misturar equipes.")
    if len({r["match_id"] for r in rows}) != len(rows):
        raise DataError("Partida duplicada no histórico de participação.")
    players = {}
    quality: Counter[str] = Counter()
    initial: dict[int, dict[str, Any]] = {}
    changes = []
    matches_with_initial = []
    for row in sorted(rows, key=lambda r: (r["match_date"], r["match_id"])):
        quality.update(row["quality"])
        for source in row["players"]:
            pid = source["player_id"]
            player = players.setdefault(pid, {
                "player_id": pid, "name": source["name"], "availability": "desconhecida",
                "match_ids": [], "event_ids": [], "matches_with_actions": 0,
                "total_actions": 0, "passes": 0, "passes_completed": 0,
                "carries": 0, "shots": 0, "pressures": 0, "xg": 0.0,
            })
            player["match_ids"].append(row["match_id"])
            player["event_ids"].extend(source["event_ids"])
            player["matches_with_actions"] += 1
            for key in ["total_actions", "passes", "passes_completed", "carries", "shots", "pressures"]:
                player[key] += source[key]
            player["xg"] = (player["xg"] + source["xg"]
                            if player["xg"] is not None and source["xg"] is not None else None)
        starting = [f for f in row["formations"] if f["event_type"] == "Starting XI"]
        if len(starting) == 1:
            f = starting[0]
            record = initial.setdefault(f["formation"], {"formation": f["formation"], "match_ids": [], "event_ids": []})
            record["match_ids"].append(row["match_id"])
            record["event_ids"].append(f["event_id"])
            matches_with_initial.append(row["match_id"])
        elif len(starting) > 1:
            quality["multiple_initial_formations_in_match"] += 1
        changes.extend(f for f in row["formations"] if f["event_type"] == "Tactical Shift")
    count = len(matches_with_initial)
    for record in initial.values():
        record.update(matches=len(record["match_ids"]),
                      share=100 * len(record["match_ids"]) / count if count else None)
    return {"team_id": rows[0]["team_id"] if rows else None,
            "match_ids": [r["match_id"] for r in rows],
            "match_dates": {str(r["match_id"]): r["match_date"] for r in rows},
            "matches_with_verified_roster": sum(r["roster_verified"] for r in rows),
            "players": sorted(players.values(), key=lambda p: (p["name"].casefold(), p["player_id"])),
            "matches_with_initial_formation": count,
            "initial_formations": [initial[k] for k in sorted(initial)],
            "formation_changes": changes, "quality": dict(quality), "limitations": list(LIMITATIONS)}
