"""Figuras exportáveis derivadas apenas do relatório; não relê eventos."""
from __future__ import annotations

import math
from textwrap import fill

from .presentation.terminology import count, date_label, number
from .presentation.coach_report import insufficient_core_evidence


def _period(profile):
    return f"{date_label(profile.get('period_start'))}–{date_label(profile.get('period_end'))}"


def _profiles(report):
    payload = getattr(report, "tactical_v3", None) or {}
    return [payload.get(side) or {} for side in ("team_profile", "opponent_profile")]


def _position(shot):
    x, y = shot.get("x"), shot.get("y")
    return (isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)
            and isinstance(y, (int, float)) and not isinstance(y, bool) and math.isfinite(y)
            and 0 <= x <= 120 and 0 <= y <= 80)


def _xg(shot):
    xg = shot.get("xg")
    return xg if (isinstance(xg, (int, float)) and not isinstance(xg, bool)
                  and math.isfinite(xg) and 0 <= xg <= 1) else None


def _pitch(ax):
    from matplotlib.patches import Rectangle
    ax.add_patch(Rectangle((0, 0), 120, 80, fill=False, edgecolor="#697b70"))
    ax.plot([60, 60], [0, 80], color="#697b70", linewidth=0.8)
    for x in (0, 102):
        ax.add_patch(Rectangle((x, 18), 18, 44, fill=False, edgecolor="#697b70", linewidth=0.8))
    ax.set_xlim(-2, 122)
    ax.set_ylim(82, -2)
    ax.set_aspect("equal")
    ax.set_xlabel("Coordenada de avanço (unidades StatsBomb; meta de referência em 120)", fontsize=8)
    ax.set_ylabel("Faixa transversal (unidades StatsBomb)", fontsize=8)
    ax.tick_params(labelsize=8)


def shot_map(report):
    import matplotlib.pyplot as plt
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import Normalize
    profiles = _profiles(report)
    figure, axes = plt.subplots(1, 2, figsize=(13.5, 6.4))
    norm = Normalize(0, 1)
    cmap = plt.get_cmap("viridis")
    for ax, profile in zip(axes, profiles):
        _pitch(ax)
        shots = [shot for shot in profile.get("shots", []) if _position(shot)]
        known = [shot for shot in shots if _xg(shot) is not None]
        unknown = [shot for shot in shots if _xg(shot) is None]
        if known:
            ax.scatter([s["x"] for s in known], [s["y"] for s in known],
                       c=[_xg(s) for s in known], s=[30 + 220 * _xg(s) for s in known],
                       cmap=cmap, norm=norm, edgecolors="#202020", linewidths=0.4, alpha=0.8)
        if unknown:
            ax.scatter([s["x"] for s in unknown], [s["y"] for s in unknown], s=40,
                       facecolors="none", edgecolors="#303030", linewidths=1.1, label="xG não disponível")
            ax.legend(loc="upper left", fontsize=7)
        if not shots:
            ax.text(60, 40, "Sem chutes com posição disponível", ha="center", va="center", fontsize=9)
        ax.set_title(f"{profile.get('team_name', 'Equipe sem identificação')}\n"
                     f"n={count(len(profile.get('match_ids', [])))} da janela; {count(len(shots), 'chute localizado', 'chutes localizados')}\n"
                     f"{_period(profile)}", fontsize=10)
    figure.suptitle("Localização das finalizações — consulta descritiva", fontsize=13)
    figure.subplots_adjust(left=0.07, right=0.87, top=0.79, bottom=0.23, wspace=0.23)
    color_axis = figure.add_axes([0.90, 0.30, 0.015, 0.40])
    from matplotlib.ticker import FuncFormatter
    figure.colorbar(ScalarMappable(norm=norm, cmap=cmap), cax=color_axis, label="Gols esperados por chute (xG)",
                    format=FuncFormatter(lambda value, _: f"{value:g}".replace(".", ",")))
    caption = ("Fonte: StatsBomb Open Data local. Cor e tamanho representam xG; círculos vazios indicam xG indisponível. "
               "Posições inválidas são excluídas. xG estima qualidade das finalizações, não chances de vitória. "
               "Coordenadas registradas: não permitem inferir esquerda/direita tática nem ocupação contínua sem bola.")
    if insufficient_core_evidence(report):
        caption = "Amostra insuficiente: não interpretar diferenças como superioridade. " + caption
    figure.text(0.07, 0.04, fill(caption, 150), fontsize=8, va="bottom")
    return figure


def progression_bars(report):
    import matplotlib.pyplot as plt
    from .v3_presentation import metric_period
    from matplotlib.ticker import FuncFormatter
    profiles = _profiles(report)
    figure, axes = plt.subplots(1, 2, figsize=(13.5, 6.4), sharey=True)
    colors = ("#367a9a", "#b36b2b")
    families = (("final_third_pass_entries", "Passes completos"), ("final_third_carry_entries", "Conduções"))
    for ax, profile in zip(axes, profiles):
        metrics = profile.get("metrics", {})
        for index, (key, label) in enumerate(families):
            metric = metrics.get(key, {})
            value = metric.get("value")
            n = metric.get("sample_size", 0)
            if value is not None and n > 0:
                ax.bar(index, value, color=colors[index], width=0.6)
                ax.annotate(number(value), (index, value), xytext=(0, 5), textcoords="offset points", ha="center", fontsize=9)
            else:
                ax.text(index, 0.05, "não disponível", ha="center", transform=ax.get_xaxis_transform(), fontsize=8)
            ax.text(index, -0.16, f"n={n}\n{metric_period(profile, metric)}", ha="center", va="top",
                    transform=ax.get_xaxis_transform(), fontsize=7)
        ax.set_xticks([0, 1], [label for _, label in families])
        ax.set_xlim(-0.6, 1.6)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}".replace(".", ",")))
        ax.set_ylabel("Entradas por 90 minutos observados")
        ax.set_title(profile.get("team_name", "Equipe sem identificação"), fontsize=11)
        ax.grid(axis="y", alpha=0.2)
        ax.set_axisbelow(True)
    maximum = max((bar.get_height() for ax in axes for bar in ax.patches), default=0)
    for ax in axes:
        ax.set_ylim(0, max(1, maximum) * 1.2)
    figure.suptitle("Entradas no terço de ataque por tipo de avanço — consulta descritiva", fontsize=13)
    figure.subplots_adjust(left=0.07, right=0.97, top=0.84, bottom=0.32, wspace=0.25)
    caption = ("Fonte: StatsBomb Open Data local. Azul: passe completo; laranja: condução. Cada barra informa jogos calculáveis "
               "e período. Entrada: bola cruza de antes do terço de ataque para dentro dele. Não mede perigo, chegada de jogadores "
               "ou eficácia. n<5: amostra insuficiente; diferenças não demonstram superioridade.")
    if insufficient_core_evidence(report):
        caption = "Amostra insuficiente: não interpretar diferenças como superioridade. " + caption
    figure.text(0.07, 0.04, fill(caption, 150), fontsize=8, va="bottom")
    return figure


def create_v3_figures(report) -> dict:
    """O chamador deve salvar/exibir e fechar todas as figuras devolvidas."""
    if not getattr(report, "tactical_v3", None):
        return {}
    return {"shot_map": shot_map(report), "progression_entries": progression_bars(report)}
