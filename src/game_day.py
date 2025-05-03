import requests
import json
import yaml
from pathlib import Path

def get_json(url: str, force: bool = False) -> dict:
    """ gets tournament json from local JSON cache (will download if missing or if force is true) """
    json_url = url.strip() + '.json'
    json_filepath = Path('JSON/' + json_url.replace("https://","").replace("http://",""))
    if force or not json_filepath.is_file():
        json_filepath.parent.mkdir(exist_ok=True, parents=True)
        resp = requests.get(url=json_url, params='')
        try:
            json_data = resp.json()
        except ValueError:
#            print('no JSON returned')
            return None
        if not json_data:
#            print ('emtpty JSON')
            return None
        with json_filepath.open(mode='w') as json_file:
            json.dump(resp.json(), json_file)
    with json_filepath.open(mode='r') as json_file:
        return json.load(json_file)

def process_tournament(tournament_url=str):
    minor_min_players = 8
    major_min_players = 16
    tournament_data = get_json(tournament_url)
    if tournament_data:
        if 'players' in tournament_data and len(tournament_data['players']) >= minor_min_players and len(tournament_data['players']) < major_min_players:
#            if 'eliminationPlayers' in tournament_data and tournament_data['eliminationPlayers']:
            print('Minor Tournament: '+tournament_url+' ['+tournament_data['date']+'] - '+tournament_data['name'])
            minor_tournaments.append({'url': tournament_url})
        if 'players' in tournament_data and len(tournament_data['players']) >= major_min_players:
#            if 'eliminationPlayers' in tournament_data and tournament_data['eliminationPlayers']:
            print('Major Tournament: '+tournament_url+' ['+tournament_data['date']+'] - '+tournament_data['name'])
            major_tournaments.append({'url': tournament_url})
    else:
        return False

minor_tournaments = []
major_tournaments = []

for id in range(1678,3585):
#    print('cobra-'+str(id))
    tournament_url = 'https://tournaments.nullsignal.games/tournaments/'+str(id)
    process_tournament(tournament_url)

for id in range(1,3393):
#    print('aesop-'+str(id))
    tournament_url = 'https://www.aesopstables.net/'+str(id)
    process_tournament(tournament_url)

with open('minor_tournaments.yml', 'w') as output_file:
    yaml.dump(minor_tournaments,output_file)

with open('major_tournaments.yml', 'w') as output_file:
    yaml.dump(major_tournaments,output_file)
