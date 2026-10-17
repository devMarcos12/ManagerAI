"""Vocabulário de futebol; valores e identificadores internos são preservados."""
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Term:
    title: str
    unit: str
    explanation: str


TERMS = {
    "xg_for": Term("Gols esperados a favor", "gols esperados por jogo", "Gols esperados (xG): soma dos valores esperados das finalizações. Não é quantidade de chances, gols reais ou probabilidade de vencer."),
    "xg_against": Term("Gols esperados concedidos", "gols esperados por jogo", "Valor esperado dos chutes adversários. Não representa os gols efetivamente sofridos."),
    "shots_for": Term("Finalizações por jogo", "por jogo", "Quantidade média de chutes registrados."),
    "shots_against": Term("Finalizações permitidas por jogo", "por jogo", "Quantidade média de chutes dos adversários."),
    "xg_per_shot": Term("Qualidade média das finalizações", "gols esperados por chute", "Valor esperado por chute; não é percentual de chutes certos."),
    "pass_accuracy": Term("Passes certos", "%", "Percentual de passes completos entre os passes tentados."),
    "pass_accuracy_under_pressure": Term("Passes certos em ações marcadas sob pressão", "%", "Somente passes explicitamente marcados como realizados sob pressão."),
    "pass_accuracy_explicit_no_pressure": Term("Passes certos em ações explicitamente sem pressão", "%", "Somente passes com ausência de pressão explicitamente marcada. Pode não haver esse registro."),
    "pass_accuracy_unmarked_pressure": Term("Passes certos sem informação de pressão", "%", "Não significa passes sem pressão; a informação não foi marcada."),
    "final_third_entries": Term("Entradas no terço de ataque", "por 90 min", "Passes completos ou conduções que levam a bola de antes do terço de ataque para dentro dele."),
    "final_third_attempts": Term("Tentativas de avançar ao terço de ataque", "por 90 min", "Inclui passes tentados que não se completaram, além das conduções."),
    "box_entries": Term("Entradas na área por passe ou condução", "por 90 min", "Passes completos ou conduções que levam a bola de fora para dentro da área. Não conta toda forma possível de entrada."),
    "pressures": Term("Tentativas de pressão registradas", "por 90 min", "Quantidade de ações registradas; maior volume não significa pressão mais eficaz."),
    "pressure_high_share": Term("Parcela da pressão realizada no terço ofensivo", "%", "Proporção das ações de pressão localizadas nessa região. Não mede sucesso da pressão."),
    "counterpressures": Term("Ações de contrapressão registradas", "por 90 min", "Ações de pressão marcadas como contrapressão; não comprova recuperação da bola."),
    "recoveries": Term("Recuperações de bola registradas", "por 90 min", "Contagem da categoria de recuperação da StatsBomb, sem afirmar sucesso de todas as ações."),
    "interceptions": Term("Interceptações registradas", "por 90 min", "Contagem dos registros, sem assumir êxito universal."),
    "duel_tackles": Term("Disputas de bola do tipo desarme", "por 90 min", "Não significa necessariamente desarme bem-sucedido."),
    "lane_low_y": Term("Ações na faixa de coordenada transversal baixa", "%", "Parcela das ações localizadas nessa faixa; não chamamos de esquerda/direita porque a orientação não foi validada."),
    "lane_central": Term("Ações na faixa central do campo", "%", "Parcela das ações localizadas na faixa central; não mede ocupação contínua dos jogadores."),
    "lane_high_y": Term("Ações na faixa de coordenada transversal alta", "%", "Parcela das ações localizadas nessa faixa; não chamamos de esquerda/direita porque a orientação não foi validada."),
}

MINIMUM_CORE_MATCHES = 5
CORE_METRICS = ("xg_for", "xg_against", "shots_for", "shots_against", "pass_accuracy", "final_third_entries")


def count(value: int, singular: str = "jogo", plural: str | None = None) -> str:
    noun = singular if value == 1 else (plural or singular + "s")
    return f"{value} {noun}"


def count_label(value: int, singular: str = "jogo", plural: str = "jogos") -> str:
    return count(value, singular, plural)


def measure(value: float | None, unit: str) -> str:
    """Une unidade e número sem espaço antes do percentual."""
    if value is None:
        return "indisponível"
    return number(value) + (unit if unit == "%" else f" {unit}")


reading = measure


PRIORITY_METRICS = ("shots_for", "xg_for", "shots_against", "xg_against", "pass_accuracy",
                    "final_third_entries", "box_entries", "pressures")


def number(value: float | None) -> str:
    if value is None:
        return "indisponível"
    return f"{value:,.2f}".translate(str.maketrans({",": ".", ".": ","}))


def date_label(value: str | None) -> str:
    return date.fromisoformat(value[:10]).strftime("%d/%m/%Y") if value else "sem histórico"
