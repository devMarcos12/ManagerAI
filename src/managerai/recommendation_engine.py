"""Regras versionadas que geram hipóteses, sem escolher uma tática ideal."""
from __future__ import annotations

from .feature_engineering import MIN_SAMPLE
from .report_schema import TacticalHypothesis, TeamProfile

RULES_VERSION = "1.0.0"


def hypotheses(own: TeamProfile, opponent: TeamProfile) -> list[TacticalHypothesis]:
    if own.sample_status == "insuficiente" or opponent.sample_status == "insuficiente":
        return []
    result = []

    def supported(profile: TeamProfile, key: str) -> bool:
        metric = profile.metrics[key]
        return metric.value is not None and metric.sample_size >= MIN_SAMPLE

    common = ["Regra exploratória sem validação causal ou de eficácia.",
              "Histórico observado não garante repetição do comportamento no jogo-alvo."]
    if supported(opponent, "final_third_entries") and supported(own, "final_third_entries") and opponent.metrics["final_third_entries"].value > 0:
        result.append(TacticalHypothesis(
            "R01_PROGRESSAO", "Investigar a proteção das zonas de chegada do adversário e ensaiar respostas às entradas no terço final.",
            "Há entradas observadas por passe completo/condução no histórico do adversário e comparação disponível com o próprio time.",
            ["opponent_profile.metrics.final_third_entries", "team_profile.metrics.final_third_entries"], common,
            ["Recuar o bloco pode conceder território e reduzir opções de saída."],
            ["Revisar sequências em vídeo antes de escolher altura de bloco ou corredores prioritários.",
             "Confirmar em treino a capacidade de cobertura dos atletas disponíveis."] ))
    if supported(opponent, "pressure_high_share") and supported(own, "pass_accuracy_under_pressure") and opponent.metrics["pressure_high_share"].value >= 30:
        result.append(TacticalHypothesis(
            "R02_PRESSAO_ALTA", "Investigar rotas de saída sob pressão e ensaiar apoios próximos como alternativa condicional.",
            "Ao menos 30% das pressões localizadas do adversário estão no terço ofensivo; há passes com pressão marcada do próprio time.",
            ["opponent_profile.metrics.pressure_high_share", "team_profile.metrics.pass_accuracy_under_pressure"],
            common + ["O limiar de 30% é uma escolha operacional exploratória, sem calibração empírica.",
                      "Volume e localização de Pressure não medem sucesso da pressão."],
            ["Aproximar apoios pode concentrar jogadores perto da bola e expor o lado oposto."],
            ["Verificar no vídeo se as pressões observadas correspondem à saída que se deseja ensaiar."] ))
    if supported(opponent, "xg_for") and supported(own, "xg_against") and opponent.metrics["xg_for"].value > 0:
        result.append(TacticalHypothesis(
            "R03_CHANCES", "Investigar a proteção da área e dos espaços de finalização antes de definir ajustes defensivos.",
            "O adversário criou chances com xG positivo; há histórico de xG concedido do próprio time para comparação.",
            ["opponent_profile.metrics.xg_for", "team_profile.metrics.xg_against"], common,
            ["Priorizar a proteção da área pode aumentar a liberdade adversária em outras zonas."],
            ["Inspecionar localização e contexto dos chutes nas partidas-fonte; a média de xG não identifica sozinha uma vulnerabilidade espacial."] ))
    return result
