import csv
import requests
import yaml

def get_cobra_json(url: str):
    json_url = url.strip() + '.json'
    resp = requests.get(url=json_url, params='')
    return resp.json()

def return_cobra_standings(json):
    standings = []
    for player in json['players']:
        standing = []
        standing.extend([player['rank'], player['name'], player['corpIdentity'], player['runnerIdentity'], player['matchPoints'], player['strengthOfSchedule'], player['extendedStrengthOfSchedule']])
        if player['rank'] <= 16:
            player_results = return_player_results_cobra(player['id'], json)
            standing.extend([str(player_results['corp_wins']), str(player_results['corp_losses']), str(player_results['corp_draws']), str(player_results['runner_wins']), str(player_results['runner_losses']), str(player_results['runner_draws'])])
        standings.append(standing)
    return standings

def return_player_results_cobra(player_id: str, json):
    player_results = { 'corp_wins': 0, 'corp_losses': 0, 'corp_draws': 0, 'runner_wins': 0, 'runner_losses': 0, 'runner_draws': 0 }
    for round in json['rounds']:
        for table in round:
            # did player play at this table?
            if table['intentionalDraw'] or table['twoForOne']:
                continue
            elif player_id == table['player1']['id']:
                scores = table['player1']
            elif player_id == table['player2']['id']:
                scores = table['player2']
            else:
                continue

            # add result
            if table['eliminationGame']:
                # add cut result
                match scores['role']:
                    case 'corp':
                        if scores['winner']:
                            player_results['corp_wins'] += 1
                        else:
                            player_results['corp_losses'] += 1
                    case 'runner':
                        if scores['winner']:
                            player_results['runner_wins'] += 1
                        else:
                            player_results['runner_losses'] += 1
            else:
                # add swiss result
                match scores['runnerScore']:
                    case 3:
                        player_results['runner_wins'] += 1
                    case 1:
                        player_results['runner_draws'] += 1
                    case 0:
                        player_results['runner_losses'] += 1
                match scores['corpScore']:
                    case 3:
                        player_results['corp_wins'] += 1
                    case 1:
                        player_results['corp_draws'] += 1
                    case 0:
                        player_results['corp_losses'] += 1
        
    return player_results

with open('config.yml', 'r') as configfile:
    config = yaml.safe_load(configfile)

    for tournament in config['tournaments']:

        if 'aesop' in tournament['url']:
            # generate standings from aesops is not implemented
            continue
        else:
            filename = tournament['name'] + '.standings.csv'
            json = get_cobra_json(tournament['url'])
            standings = return_cobra_standings(json)

        with open(filename,'w',newline='') as f:
            w = csv.writer(f)
            w.writerows(standings)

