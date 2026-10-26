"""CLI local; execução via PYTHONPATH=src python3 -m managerai."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from .data_inventory import inventory, load_season, team_ids
from .data_loader import DataError, LocalData
from .pipeline import analyze, audit
from .report_renderer import render_markdown
from .report_schema import AnalysisRequest
from .statsbomb_provisioning import verify_snapshot

DEFAULT_DATA = Path(__file__).resolve().parents[2] / "open-data" / "data"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ManagerAI — apoio histórico pré-jogo, sem rede ou modelo treinado.")
    p.add_argument("--data-root", type=Path,
                   default=Path(os.environ.get("MANAGERAI_DATA_ROOT", str(DEFAULT_DATA))),
                   help="Diretório data do clone StatsBomb; padrão MANAGERAI_DATA_ROOT ou open-data/data")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("verify-data", help="Verifica revisão, licença, estrutura e cobertura StatsBomb (JSON)")
    sub.add_parser("catalog", help="Inventário de cobertura e arquivos sem catálogo (JSON)")
    for command in ("teams", "matches", "audit", "analyze"):
        q = sub.add_parser(command)
        q.add_argument("--competition-id", type=int, required=True)
        q.add_argument("--season-id", type=int, required=True)
        if command == "analyze":
            q.add_argument("--team-id", type=int, required=True)
            q.add_argument("--opponent-id", type=int, required=True)
            cutoff = q.add_mutually_exclusive_group(required=True)
            cutoff.add_argument("--cutoff-date")
            cutoff.add_argument("--target-match-id", type=int)
            q.add_argument("--window", type=int, default=10)
            q.add_argument("--v3", action="store_true", help="Acrescenta análise tática por eventos e gráficos locais; preserva campos V1/V2")
            q.add_argument("--venue", default="desconhecido", choices=["casa", "fora", "neutro", "desconhecido"])
            q.add_argument("--match-context", default="regular", choices=["regular", "clássico", "eliminatório", "decisivo", "outro"])
            q.add_argument("--strategic-objective", default="equilibrado", choices=["equilibrado", "pressionar alto", "proteger vantagem", "buscar gol", "outro"])
            q.add_argument("--unavailable-player-id", type=int, action="append", default=[])
            q.add_argument("--notes", default="")
            q.add_argument("--output-dir", type=Path, required=True, help="Diretório novo para report.json e report.md; não sobrescreve")
    return p


def main(argv: list[str] | None = None) -> int:
    p = parser()
    args = p.parse_args(argv)
    try:
        data = LocalData(args.data_root)
        if args.command == "verify-data":
            result = verify_snapshot(args.data_root)
            print(json.dumps(result, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2))
            return 0 if result["status"] == "compatível" else 2
        if args.command == "catalog":
            result = inventory(data)
        elif args.command == "audit":
            result = audit(args.data_root, args.competition_id, args.season_id)
        elif args.command in ("teams", "matches"):
            s = load_season(data, args.competition_id, args.season_id)
            if args.command == "teams":
                result = [{"team_id": tid, "name": name,
                           "matches_with_events": sum(tid in team_ids(m) and data.exists("events", m["match_id"]) for m in s.matches)} for tid, name in sorted(s.teams.items())]
            else:
                result = [{"match_id": m["match_id"], "date": m["match_date"], "kick_off": m.get("kick_off"),
                           "home_team_id": team_ids(m)[0], "away_team_id": team_ids(m)[1],
                           "events_exists": data.exists("events", m["match_id"]),
                           "lineups_exists": data.exists("lineups", m["match_id"])}
                          for m in sorted(s.matches, key=lambda m: (m["match_date"], m["match_id"]))]
        else:
            dest = args.output_dir.resolve()
            if dest == data.root or dest.is_relative_to(data.root):
                raise ValueError("A saída deve ficar fora da raiz dos dados brutos.")
            if dest.exists():
                raise ValueError("Diretório de saída já existe; escolha outro para preservar os resultados.")
            request = AnalysisRequest(args.competition_id, args.season_id, args.team_id, args.opponent_id,
                                      args.cutoff_date, args.target_match_id, args.window, args.venue,
                                      args.match_context, args.strategic_objective, tuple(args.unavailable_player_id), args.notes)
            report = analyze(args.data_root, request, include_v3=args.v3)
            structured, readable = report.to_json(), render_markdown(report)
            figures = {}
            if args.v3:
                from .v3_plots import create_v3_figures
                figures = create_v3_figures(report)
                readable += "\n## Visualizações\n\n" + "\n\n".join(f"![{name}]({name}.png)" for name in figures) + "\n"
            dest.mkdir(parents=True, exist_ok=False)
            (dest / "report.json").write_text(structured, encoding="utf-8")
            (dest / "report.md").write_text(readable, encoding="utf-8")
            if figures:
                import matplotlib.pyplot as plt
                try:
                    for name, figure in figures.items():
                        figure.savefig(dest / f"{name}.png", dpi=150, bbox_inches="tight")
                finally:
                    for figure in figures.values():
                        plt.close(figure)
            result = {"report_json": str(dest / "report.json"), "report_markdown": str(dest / "report.md"),
                      "matches_analyzed_team": report.metadata["matches_analyzed_team"],
                      "matches_analyzed_opponent": report.metadata["matches_analyzed_opponent"],
                      "hypotheses": len(report.tactical_hypotheses)}
            if args.v3:
                result["v3_hypotheses"] = len(report.tactical_v3["hypotheses"])
                result["schema_version"] = report.schema_version
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except ImportError as exc:
        print(f"Erro: dependência opcional ausente ({exc.name}). Para gráficos V3, execute python -m pip install '.[v3]' na raiz, usando o Python do ambiente virtual.", file=sys.stderr)
        return 2
    except (DataError, ValueError, OSError, KeyError, TypeError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
