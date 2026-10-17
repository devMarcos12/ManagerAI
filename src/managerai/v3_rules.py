"""Regras exploratórias 3.0.0; limiares operacionais, sem eficácia validada."""
from .presentation.coach_report import insufficient_core_evidence
from .feature_engineering import finite
from .presentation.terminology import number, count


def hypotheses_v3(report, own: dict, opponent: dict, minimum_matches: int = 5) -> list[dict]:
    if type(minimum_matches) is not int or minimum_matches < 1:
        raise ValueError("Mínimo de jogos deve ser inteiro positivo.")
    if insufficient_core_evidence(report):
        return []
    result = []

    def eligible(profile, *keys):
        return all(finite(profile['metrics'].get(k, {}).get('value'))
                   and finite(profile['metrics'][k].get('denominator'))
                   and profile['metrics'][k]['denominator'] > 0
                   and profile['metrics'][k]['sample_size'] >= minimum_matches for k in keys)

    def reference(side, keys):
        return [f'tactical_v3.{side}_profile.metrics.{k}' for k in keys]

    def add(rule, title, observation, action, condition, references, risk):
        result.append(dict(rule_id=rule, title=title, observation=observation, action=action,
                           condition=condition, evidence_metrics=references,
                           preconditions=['Conferir em vídeo as ações e seus destinos antes de escolher o ajuste.',
                                          'Testar em treino com os jogadores historicamente observados, sem presumir disponibilidade no alvo.'],
                           risks=[risk], limitations=['Associação descritiva, sem demonstração de eficácia ou causalidade.',
                           f'Adversários, datas e contextos das janelas podem diferir; {count(minimum_matches)} é somente um mínimo operacional.'],
                           confidence_level='limitada'))

    keys = ('final_third_pass_entries', 'final_third_carry_entries')
    if eligible(own, *keys) and eligible(opponent, *keys):
        a, b = (opponent['metrics'][k] for k in keys)
        total = a['value'] + b['value']
        # Comparing shares requires exactly the same match/exposure denominators.
        if total > 0 and a['match_ids'] == b['match_ids'] and a['denominator'] == b['denominator']:
            share = 100 * a['value'] / total
            if share >= 60:
                own_a = own['metrics'][keys[0]]
                add('V3_ENTRADAS_PASSE', 'Avaliar a proteção das recepções no terço de ataque',
                    f"{opponent['team_name']}: {number(a['value'])} entradas por passe e {number(b['value'])} por condução a cada 90 min "
                    f"({count(a['sample_size'])}); passes representam {number(share)}% dessas entradas. "
                    f"{own['team_name']}: {number(own_a['value'])} entradas por passe a cada 90 min ({count(own_a['sample_size'])}).",
                    'Selecionar em vídeo as recepções que cruzam o limite do terço de ataque e ensaiar cobertura do receptor e da linha de passe.',
                    f'Pelo menos {count(minimum_matches)} calculáveis em cada indicador citado; passes representam ao menos 60% das entradas observadas do adversário.',
                    reference('opponent', keys) + reference('team', (keys[0],)),
                    'Fechar linhas de passe pode abrir espaço para conduções; a contagem não identifica sozinha a zona mais perigosa.')

    keys = ('shots_box_share', 'xg_box')
    if eligible(own, 'shots_box_share') and eligible(opponent, *keys):
        share, xg = (opponent['metrics'][k] for k in keys)
        if share['value'] >= 60:
            own_share = own['metrics']['shots_box_share']
            add('V3_CHUTES_AREA', 'Rever a proteção das zonas de finalização dentro da área',
                f"{opponent['team_name']}: {number(share['value'])}% dos chutes localizados partiram da área "
                f"({count(share['sample_size'])}); gols esperados desses chutes: {number(xg['value'])} por jogo "
                f"({count(xg['sample_size'])}). {own['team_name']}: {number(own_share['value'])}% dos chutes localizados "
                f"partiram da área ({count(own_share['sample_size'])}).",
                'Usar o mapa para selecionar lances dentro da área e testar proteção do espaço antes do chute, após rever o início de cada jogada.',
                f'Pelo menos {count(minimum_matches)} em cada métrica citada; ao menos 60% dos chutes localizados do adversário partiram da área.',
                reference('opponent', keys) + reference('team', ('shots_box_share',)),
                'Concentrar a proteção na área pode permitir finalizações de fora e não elimina a qualidade dos chutes concedidos.')
    return result
