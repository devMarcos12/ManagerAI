"""Sequências observadas, versão 3.0.0; não inferem causalidade ou posse real.

``sequence_summary(match, events, team_id)`` recebe somente um jogo já selecionado
pelo corte temporal. Ordena por index (nunca por número de posse), considera os
períodos 1/2 e divide blocos contíguos pela tupla (period, possession,
possession_team.id). Um ID que reaparece inicia outro bloco. O denominador é
"blocos de posse com ações ofensivas próprias registradas": Pass completo,
Carry ou Shot. Pressure, ações rivais e passes incompletos não alimentam esse
denominador. Não é o total de posses reais nem percentual de tempo com a bola.

Entradas usam a geometria V1: cruzar x=80 ou entrar em x>=102, 18<=y<=62,
por passe completo/condução com ambos os extremos válidos. Evidências associam
até três ações próprias anteriores no mesmo bloco, sem causalidade; interrompem
o encadeamento em passe incompleto e ações próprias não Pass/Carry. Não estimam
recuperação após pressão, eficácia, disponibilidade ou tática ideal.

Erros estruturais/contextuais, relógios decrescentes no período e ações ofensivas
próprias sem geometria invalidam blocos. Para não contar observações incompletas
como total, qualquer bloco inválido torna contadores e proporções do jogo None.
Blocos íntegros continuam disponíveis para inspeção, com qualidade explícita.
Um fluxo vazio/sem período regulamentar também é indisponível. Fluxo íntegro
sem blocos próprios observados tem contadores zero, mas proporções None.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from .data_inventory import team_ids
from .data_loader import DataError
from .feature_engineering import in_box, point, seconds


LIMITATIONS = [
    "Blocos de posse com ações ofensivas registradas não representam todas as posses reais nem tempo de posse.",
    "Ações anteriores e entrada/finalização pertencem ao mesmo bloco observado; a associação não demonstra causalidade.",
    "Tentativas de pressão e eventos adversários não são atribuídos como ações ofensivas da equipe titular da posse.",
    "Somente os dois tempos regulamentares; faixas registradas não comprovam esquerda/direita tática.",
]


def _object_id(value: Any) -> Any:
    return value.get("id") if isinstance(value, dict) else None


def sequence_summary(match: dict[str, Any], events: list[dict[str, Any]], team_id: int) -> dict[str, Any]:
    """Retorna contagens por bloco e eventos-fonte; não lê arquivos ou dados futuros."""
    quality: Counter[str] = Counter()
    output: dict[str, Any] = {
        "match_id": match["match_id"], "match_date": match["match_date"],
        "team_id": team_id, "valid_blocks": None, "entry_blocks": None,
        "shot_blocks": None, "entry_block_share": None, "shot_block_share": None,
        "blocks": [], "quality": {}, "limitations": list(LIMITATIONS),
    }
    teams = team_ids(match)
    if team_id not in teams:
        raise DataError("Equipe de sequência incompatível com a partida.")
    ids, indices = set(), set()
    for event in events:
        if not isinstance(event, dict):
            quality["invalid_event_object"] += 1
            continue
        eid, index = event.get("id"), event.get("index")
        if (not isinstance(eid, str) or not eid or eid in ids
                or type(index) is not int or index < 1 or index in indices):
            quality["invalid_event_identity_or_index"] += 1
        ids.add(eid) if isinstance(eid, str) else None
        indices.add(index) if type(index) is int else None
    if quality:
        output["quality"] = dict(quality)
        return output
    ordered = sorted(events, key=lambda e: e["index"])
    current = None
    blocks: list[dict[str, Any]] = []
    previous_period = 0
    clock_by_period: dict[int, float] = {}
    regulation_events = 0
    for event in ordered:
        period = event.get("period")
        if type(period) is not int or period < 1 or period > 5:
            quality["invalid_period"] += 1
            current = None
            continue
        if period not in (1, 2):
            current = None
            continue
        regulation_events += 1
        possession = event.get("possession")
        owner = _object_id(event.get("possession_team"))
        key = (period, possession, owner)
        if current is None or current["key"] != key:
            current = {"key": key, "block_id": len(blocks) + 1,
                       "period": period, "possession_id": possession, "owner_team_id": owner,
                       "event_ids": [], "offensive_action_ids": [], "entries": [],
                       "shots": [], "preceding": [], "valid": True}
            blocks.append(current)
        current["event_ids"].append(event["id"])
        if (type(possession) is not int or possession < 1
                or type(owner) is not int or owner not in teams):
            quality["invalid_possession_context"] += 1
            current["valid"] = False
        tid = _object_id(event.get("team"))
        if type(tid) is not int or tid not in teams:
            quality["invalid_event_team"] += 1
            current["valid"] = False
        try:
            clock = seconds(event.get("timestamp"))
            if period < previous_period or clock < clock_by_period.get(period, 0):
                raise DataError("Relógio/contexto de período decrescente.")
            clock_by_period[period] = clock
        except DataError:
            quality["invalid_or_decreasing_timestamp"] += 1
            current["valid"] = False
        previous_period = period
        type_object = event.get("type")
        typ = type_object.get("name") if isinstance(type_object, dict) else None
        if not isinstance(typ, str) or not typ:
            quality["invalid_event_type"] += 1
            current["valid"] = False
        if tid != team_id or owner != team_id:
            continue
        if typ == "Shot":
            current["offensive_action_ids"].append(event["id"])
            current["shots"].append({"event_id": event["id"], "type": typ,
                                     "location": list(point(event.get("location"))) if point(event.get("location")) else None,
                                     "preceding_actions": list(current["preceding"][-3:])})
            current["preceding"] = []
            continue
        if typ not in ("Pass", "Carry"):
            # Administrative events and receipts do not interrupt ball movement;
            # other own on-ball actions do, rather than bridge a failed dribble.
            if typ not in ("Ball Receipt*", "Starting XI", "Tactical Shift", "Half Start"):
                current["preceding"] = []
            continue
        payload = event.get(typ.lower())
        if not isinstance(payload, dict):
            quality["offensive_action_missing_payload"] += 1
            current["valid"] = False
            current["preceding"] = []
            continue
        if typ == "Pass" and payload.get("outcome"):
            current["preceding"] = []
            continue
        start, end = point(event.get("location")), point(payload.get("end_location"))
        if start is None or end is None:
            quality["offensive_action_invalid_geometry"] += 1
            current["valid"] = False
            current["preceding"] = []
            continue
        action = {"event_id": event["id"], "type": typ,
                  "start": list(start), "end": list(end)}
        current["offensive_action_ids"].append(event["id"])
        final_third = start[0] < 80 <= end[0]
        box = not in_box(start) and in_box(end)
        if final_third or box:
            current["entries"].append({**action, "final_third": final_third,
                                       "box": box, "preceding_actions": list(current["preceding"][-3:])})
        current["preceding"].append(action)
        current["preceding"] = current["preceding"][-3:]
    if not regulation_events:
        quality["no_regulation_events"] += 1
    valid = [b for b in blocks if b["valid"] and b["owner_team_id"] == team_id and b["offensive_action_ids"]]
    for block in valid:
        block.pop("key")
        block.pop("preceding")
    output["blocks"] = valid
    output["quality"] = dict(quality)
    if not quality:
        count = len(valid)
        entries = sum(bool(b["entries"]) for b in valid)
        shots = sum(bool(b["shots"]) for b in valid)
        output.update(valid_blocks=count, entry_blocks=entries, shot_blocks=shots,
                      entry_block_share=100 * entries / count if count else None,
                      shot_block_share=100 * shots / count if count else None)
    return output
