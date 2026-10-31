"""Opções canônicas compartilhadas pelo Core e OpenAPI; sem dependências."""
from typing import Literal, get_args

Venue = Literal["casa", "fora", "neutro", "desconhecido"]
MatchContext = Literal["regular", "clássico", "eliminatório", "decisivo", "outro"]
Objective = Literal["equilibrado", "pressionar alto", "proteger vantagem", "buscar gol", "outro"]
Strategy = Literal["equilibrada", "proteger_area", "saida_sob_pressao", "proteger_progressao"]
PlanId = Literal["R01_PROGRESSAO", "R02_PRESSAO_ALTA", "R03_CHANCES", "V3_ENTRADAS_PASSE", "V3_CHUTES_AREA"]
ExplanationMode = Literal["none", "optional", "required"]
Availability = Literal["available", "unavailable", "unknown"]
VENUES, CONTEXTS, OBJECTIVES = get_args(Venue), get_args(MatchContext), get_args(Objective)
STRATEGIES, PLAN_IDS = get_args(Strategy), frozenset(get_args(PlanId))
