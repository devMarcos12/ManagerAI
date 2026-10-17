"""Auditoria somente leitura; imprime JSON no stdout, não altera o dataset."""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import math

ROOT = Path('open-data/data')

def read(relative):
    return json.loads((ROOT / relative).read_text())

def valid(point):
    return (isinstance(point, list) and len(point) >= 2
            and all(isinstance(v, (float, int)) and not isinstance(v, bool)
                    and math.isfinite(v) for v in point[:2])
            and 0 <= point[0] <= 120 and 0 <= point[1] <= 80)

result = {'method': 'All catalog metadata; full event/lineup content only for PL 2015/16 and La Liga 2020/21. No target exclusion: this is dataset auditing, not pre-match analysis.', 'catalog': [], 'field_audit': {}}
for competition in read('competitions.json'):
    cid, sid = competition['competition_id'], competition['season_id']
    matches = read(f'matches/{cid}/{sid}.json')
    c = {'competition_id': cid, 'season_id': sid,
         'competition': competition['competition_name'], 'season': competition['season_name'],
         'matches': len(matches), 'events_files': 0, 'lineups_files': 0, 'three_sixty_files': 0}
    for kind, key in [('events', 'events_files'), ('lineups', 'lineups_files'), ('three-sixty', 'three_sixty_files')]:
        c[key] = sum((ROOT / kind / f"{m['match_id']}.json").is_file() for m in matches)
    if cid == 11:
        c['team_coverage'] = {}
        for name in ['Real Madrid', 'Barcelona']:
            selected = sorted([m for m in matches if any(m[f'{s}_team'][f'{s}_team_name'] == name for s in ['home', 'away'])], key=lambda m: (m['match_date'], m['match_id']))
            earlier = [m for m in selected if m['match_date'] < '2021-04-10']
            c['team_coverage'][name] = {'all_matches': len(selected), 'before_2021_04_10': len(earlier), 'last10': [{'match_id': m['match_id'], 'date': m['match_date'], 'events_available': (ROOT/'events'/f"{m['match_id']}.json").is_file()} for m in earlier[-10:]]}
    result['catalog'].append(c)
    if (cid, sid) not in [(2, 27), (11, 90)]:
        continue
    counts, types, counters, per_match = Counter(), Counter(), defaultdict(Counter), []
    orientation = defaultdict(lambda: defaultdict(Counter))
    sources = {}
    for match in matches:
        mid = match['match_id']
        sources[str(mid)] = hashlib.sha256((ROOT/'events'/f'{mid}.json').read_bytes()).hexdigest()
        events = read(f'events/{mid}.json')
        lineups = read(f'lineups/{mid}.json')
        players = {l['team_id']: {p['player_id'] for p in l['lineup']} for l in lineups}
        teams = {match[f'{s}_team'][f'{s}_team_id'] for s in ['home', 'away']}
        ids = Counter(e.get('id') for e in events)
        counts['duplicate_event_ids'] += sum(v-1 for v in ids.values())
        prior_possession = None
        possession_teams = defaultdict(set)
        observed = Counter()
        for lineup in lineups:
            for player in lineup['lineup']:
                counts['lineup_player_records'] += 1
                counts['lineup_player_with_positions'] += bool(player.get('positions'))
        for e in events:
            name = e.get('type', {}).get('name', 'MISSING')
            types[name] += 1
            counts['events'] += 1
            tid = e.get('team', {}).get('id')
            pid = e.get('player', {}).get('id')
            counts['invalid_team'] += tid not in teams
            counts['with_player'] += pid is not None
            counts['player_not_in_lineup_team'] += pid is not None and pid not in players.get(tid, set())
            for field in ['possession', 'possession_team', 'timestamp', 'duration', 'location', 'under_pressure', 'counterpress', 'tactics']:
                counts[f'with_{field}'] += field in e
            possession, ptid = e.get('possession'), e.get('possession_team', {}).get('id')
            counts['invalid_possession_team'] += ptid not in teams
            if isinstance(possession, int):
                possession_teams[(e.get('period'), possession)].add(ptid)
                counts['possession_id_decreases'] += prior_possession is not None and possession < prior_possession
                prior_possession = possession
            duration = e.get('duration')
            if duration is not None:
                counts['invalid_duration'] += not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration < 0
            if 'location' in e:
                counts['invalid_location'] += not valid(e['location'])
            detail = counters[name]
            detail['events'] += 1
            detail['valid_location'] += valid(e.get('location'))
            detail['with_player'] += pid is not None
            observed[name] += 1
            if name in ['Pass', 'Carry']:
                payload = e.get(name.lower())
                detail['with_payload'] += isinstance(payload, dict)
                detail['valid_end_location'] += isinstance(payload, dict) and valid(payload.get('end_location'))
                if name == 'Pass' and isinstance(payload, dict):
                    detail['no_outcome'] += not payload.get('outcome')
                    detail['with_recipient'] += isinstance(payload.get('recipient'), dict)
                    detail['outcome_' + payload.get('outcome', {}).get('name', 'Complete_convention')] += 1
            if name == 'Shot':
                p = e.get('shot', {})
                xg = p.get('statsbomb_xg')
                detail['valid_xg'] += isinstance(xg, (float, int)) and math.isfinite(xg) and 0 <= xg <= 1
                detail['valid_end_location'] += valid(p.get('end_location'))
                if valid(e.get('location')):
                    o = orientation[str(e.get('period'))][str(tid)]
                    o['shots'] += 1
                    o['start_x_ge_80'] += e['location'][0] >= 80
                    o['start_x_lt_60'] += e['location'][0] < 60
                    o['sum_start_x'] += e['location'][0]
                    end = p.get('end_location')
                    if isinstance(end, list) and len(end) >= 2:
                        o['end_x_120'] += end[0] == 120
                        o['end_x_0'] += end[0] == 0
            if name in ['Starting XI', 'Tactical Shift']:
                tactics = e.get('tactics', {})
                detail['formation_present'] += isinstance(tactics.get('formation'), int)
                detail['lineup_present'] += bool(tactics.get('lineup'))
            if name == 'Ball Recovery':
                detail['failure_true'] += e.get('ball_recovery', {}).get('recovery_failure') is True
            if name == 'Pressure':
                detail['team_matches_possession_team'] += tid == ptid
                detail['counterpress_true'] += e.get('counterpress') is True
        counts['possession_blocks'] += len(possession_teams)
        counts['possession_blocks_multiple_teams'] += sum(len(v)>1 for v in possession_teams.values())
        per_match.append({'match_id': mid, 'events': len(events), 'types': dict(observed)})
    result['field_audit'][f'{cid}/{sid}'] = {'counts': dict(counts), 'types': dict(types), 'by_type': {k:dict(v) for k,v in counters.items()}, 'shots_by_period_team': {p:{t:dict(v) for t,v in ts.items()} for p,ts in orientation.items()}, 'per_match': per_match, 'events_sha256': sources}
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
