"""Análise aditiva dos mesmos jogos, verificando integridade entre leituras."""
from dataclasses import fields, asdict
from statistics import median, stdev

from .data_inventory import load_season
from .data_loader import LocalData, DataError
from .feature_engineering import match_features
from .temporal import select_history
from .v3_schema import AnalysisReportV3, VALIDATED_RECUTS
from .report_schema import MetricEvidence
from .v3_rules import hypotheses_v3


def extend_report(root, report):
    if (report.request.competition_id, report.request.season_id) not in VALIDATED_RECUTS:
        raise DataError('V3 disponível somente para recorte auditado: Premier League 2015/16 ou La Liga 2020/21. Use a análise anterior para outros recortes.')
    from .v3_features import analyze_match_v3, aggregate_v3, V3_METRICS
    from .v3_sequences import sequence_summary
    from .v3_history import historical_participation, aggregate_history
    data = LocalData(root)
    season = load_season(data, report.request.competition_id, report.request.season_id)
    histories, _ = select_history(season, report.request)
    cache, profiles = {}, {}
    for tid, history in histories.items():
        rows, sequences, history_rows = [], [], []
        for match in history:
            mid = match['match_id']
            if not data.exists('events', mid):
                continue
            if mid not in cache:
                events = data.events(mid)
                lineups = data.lineups(mid) if data.exists('lineups', mid) else None
                features, _ = match_features(match, events, lineups)
                cache[mid] = (events, features, lineups)
            events, features, lineups = cache[mid]
            rows.append(analyze_match_v3(match, events, tid, features[tid]['minutes']))
            sequences.append(sequence_summary(match, events, tid))
            history_rows.append(historical_participation(match, events, lineups, tid))
        profile = aggregate_v3(tid, season.teams[tid], rows)
        profile['sequences'] = sequences
        profile['sequence_metrics'] = aggregate_sequences(sequences)
        profile['historical'] = aggregate_history(history_rows)
        profiles[tid] = profile
    original = {x['path']: x['sha256'] for x in report.methodology['sources']}
    if any(original.get(path) != digest for path, digest in data.sources.items()):
        raise DataError('Os dados mudaram entre a análise original e a extensão V3; execute novamente.')
    own, opponent = profiles[report.request.team_id], profiles[report.request.opponent_id]
    if own['match_ids'] != report.team_profile.match_ids or opponent['match_ids'] != report.opponent_profile.match_ids:
        raise DataError('A cobertura mudou entre a análise original e a extensão V3; execute novamente.')
    payload = dict(formula_version='3.0.0', rules_version='3.0.0', team_profile=own, opponent_profile=opponent,
                   hypotheses=hypotheses_v3(report, own, opponent), metric_definitions=V3_METRICS,
                   methodology=dict(
                       minimum_sample_matches=5,
                       sample_policy='Hipóteses exigem cinco jogos em cada métrica citada e suficiência das métricas centrais de ambas as equipes; evidência limitada.',
                       temporal_policy=report.methodology['temporal_policy'],
                       aggregation='Taxas/proporções agregam numeradores e denominadores somente dos jogos calculáveis; mediana e desvio entre jogos, n=1 sem desvio.',
                       coordinate_policy='Plano registrado 120×80; direção de ataque x crescente para a meta [120,40], sustentada pela auditoria nos dois recortes. Sem espelhar períodos. Faixas y não equivalem a esquerda/direita tática.',
                       progression='Progressivo: passe completo ou condução reduz distância euclidiana à meta [120,40] em pelo menos 10 unidades do plano; limiar operacional, não metros nem eficácia.',
                       pressure='Pressão espacial e recuperação registrada apresentadas separadamente. Não mede sucesso nem atribui causalidade entre eventos.',
                       context_policy=report.methodology['context_policy'],
                       sequence_policy='Blocos contíguos por período, ID e equipe de posse, em ordem de index. Ações ofensivas do próprio titular apenas; associações sem causalidade.',
                       sources=[dict(path=p, sha256=h) for p,h in sorted(data.sources.items())],
                       data_fingerprint=data.fingerprint(),
                       not_supported=['Tracking ou posicionamento sem bola', 'Eficácia de pressão', 'Disponibilidade no alvo e escalação ideal', 'Formação vencedora', 'Probabilidade de vitória'],
                       attribution=report.methodology['attribution']))
    values = {f.name: getattr(report, f.name) for f in fields(report) if f.name != 'schema_version'}
    enriched = AnalysisReportV3(**values, tactical_v3=payload)
    enriched.to_dict()
    return enriched


def aggregate_sequences(rows):
    """Somente jogos integralmente calculáveis; blocos não equivalem a posses reais."""
    definitions = {
        'observed_blocks': ('valid_blocks', None),
        'entry_block_share': ('entry_blocks', 'valid_blocks'),
        'shot_block_share': ('shot_blocks', 'valid_blocks'),
    }
    result = {}
    for key, (num, den) in definitions.items():
        valid = [r for r in rows if r.get(num) is not None and (den is None or r.get(den, 0) > 0)]
        multiplier = 100 if den else 1
        values = [multiplier*r[num]/r[den] if den else r[num] for r in valid]
        numerator = sum(r[num] for r in valid) if valid else None
        denominator = sum(r[den] for r in valid) if den and valid else len(valid) if valid else None
        result[key] = asdict(MetricEvidence(
            key, multiplier*numerator/denominator if valid else None,
            '%' if den else 'blocos observados/jogo', len(valid), [r['match_id'] for r in valid],
            numerator, denominator, median(values) if values else None,
            stdev(values) if len(values)>1 else None,
            [dict(match_id=r['match_id'], match_date=r['match_date'], value=v,
                  numerator=r[num], denominator=r[den] if den else 1) for r,v in zip(valid,values)], '3.0.0'))
    return result
