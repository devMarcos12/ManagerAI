"""Extensão opt-in: consumidores V1/V2 mantêm contrato byte a byte."""
from dataclasses import dataclass, field
from typing import Any
from .report_schema import AnalysisReport


# Recortes com auditoria integral de campos e orientação nesta entrega.
VALIDATED_RECUTS = frozenset({(2, 27), (11, 90)})


@dataclass
class AnalysisReportV3(AnalysisReport):
    schema_version: str = "1.1.0"
    tactical_v3: dict[str, Any] = field(default_factory=dict)
