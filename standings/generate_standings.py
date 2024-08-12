import csv
import requests
import yaml

def get_json(url: str):
    json_url = url.strip() + '.json'
    resp = requests.get(url=json_url, params='')
    return resp.json()

# takes an identity name and standardises it (if necessary)
def standardise_identity(identity: str) -> str:
    match identity:
        case 'Rielle "Kit" Peddler: Transhuman':
            identity = 'Rielle “Kit” Peddler: Transhuman'
        case 'Esa Afontov: Eco-Insurrectionist':
            identity = 'Esâ Afontov: Eco-Insurrectionist'
        case 'Tao Salonga: Telepresence Magician':
            identity = 'Tāo Salonga: Telepresence Magician'
        case 'Ayla "Bios" Rahim: Simulant Specialist':
            identity ='Ayla “Bios” Rahim: Simulant Specialist'
        case 'Sebastiao Souza Pessoa: Activist Organizer':
            identity = 'Sebastião Souza Pessoa: Activist Organizer'
        case 'Ken "Express" Tenma: Disappeared Clone':
            identity = 'Ken “Express” Tenma: Disappeared Clone'
        case 'Rene "Loup" Arcemont: Party Animal':
            identity = 'René “Loup” Arcemont: Party Animal'
    return identity

# takes an identity and returns the faction anem of that identity
def get_faction(id_info, identity: str) -> str:
    faction = 'unknown'

    return faction

def return_standings(json, tournament_sw: str, tournament_name: str, id_info):
    standings = []
    standings.append(['tournament','rank','name','corp_name','corp_wins','corp_losses','corp_draws','runner_name','runner_wins','runner_losses','runner_draws','matchPoints','SoS','xSoS','corp_ID','corp_faction','runner_ID','runner_faction'])
    for player in json['players']:
        standing = []
        match tournament_sw:
            case 'cobra':
                player_results = return_player_results_cobra(player['id'], json)
            case 'aesops':
                player_results = return_player_results_aesops(player['id'], json)
        
        runner_id = standardise_identity(player['runnerIdentity'])
        runner_faction = id_info[runner_id].get('faction','unknown')
        runner_name = id_info[runner_id].get('short_name','unknown')
        corp_id = player['corpIdentity']
        corp_faction = id_info[corp_id].get('faction','unknown')
        corp_name = id_info[corp_id].get('short_name','unknown')


        standing.extend([tournament_name, player['rank'], player['name'], corp_name, str(player_results['corp_wins']), str(player_results['corp_losses']), str(player_results['corp_draws']), runner_name, str(player_results['runner_wins']), str(player_results['runner_losses']), str(player_results['runner_draws']), player['matchPoints'], player['strengthOfSchedule'], player['extendedStrengthOfSchedule'], corp_id, corp_faction, runner_id, runner_faction])
        standings.append(standing)
    return standings

def return_player_results_aesops(player_id: str, json):
    player_results = { 'corp_wins': 0, 'corp_losses': 0, 'corp_draws': 0, 'runner_wins': 0, 'runner_losses': 0, 'runner_draws': 0 }
    for round in json['rounds']:
        for table in round:
            # did player play at this table?
            if player_id == table['corpPlayer']:
                if 'eliminationGame' in table and table['eliminationGame']:
                    if player_id == table['winner_id']:
                        player_results['corp_wins'] += 1
                    else:
                        player_results['corp_losses'] += 1
                else:
                    match table['corpScore']:
                        case "3":
                            player_results['corp_wins'] += 1
                        case "1":
                            player_results['corp_draws'] += 1
                        case "0":
                            player_results['corp_losses'] += 1
            elif player_id == table['runnerPlayer']:
                if 'eliminationGame' in table and table['eliminationGame']:
                    if player_id == table['winner_id']:
                        player_results['runner_wins'] += 1
                    else:
                        player_results['runner_losses'] += 1
                else:
                    match table['runnerScore']:
                        case "3":
                            player_results['runner_wins'] += 1
                        case "1":
                            player_results['runner_draws'] += 1
                        case "0":
                            player_results['runner_losses'] += 1
                        case _:
                            player_results['runner_draws'] += 1
    return player_results

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

with open('config.yml', 'r') as configfile, open('identities.yml', 'r') as idFile:
    config = yaml.safe_load(configfile)
    id_info = yaml.safe_load(idFile)
    standings_dir = 'results/standings/'

    for tournament in config['tournaments']:
        filename = standings_dir + tournament['name'] + '.standings.csv'
        json = get_json(tournament['url'])

        if 'aesop' in tournament['url']:
            standings = return_standings(json, 'aesops', tournament['name'], id_info)
        else:
            standings = return_standings(json, 'cobra', tournament['name'], id_info)

        with open(filename,'w',newline='') as f:
            w = csv.writer(f)
            w.writerows(standings)

