import csv
import yaml
import requests
import json
import datetime
from pathlib import Path
import argparse
from netrunner.tournament import Tournament,AesopsTournament,CobraTournament,ABRTournament
from netrunner.player import TournamentPlayer,Player

def get_json(url: str, force: bool = False) -> dict:
    """ gets tournament json from local JSON cache (will download if missing or if force is true) """
    json_url = url.strip() + '.json'
    json_filepath = Path('JSON/' + json_url.replace("https://","").replace("http://",""))
    if force or not json_filepath.is_file():
        json_filepath.parent.mkdir(exist_ok=True, parents=True)
        resp = requests.get(url=json_url, params='')
        with json_filepath.open(mode='w') as json_file:
            json.dump(resp.json(), json_file)
    with json_filepath.open(mode='r') as json_file:
        return json.load(json_file)
    
def find_abr_tournament(date: datetime.date, name: str, size: int, force: bool = False) -> dict:
    """ use the abr API to find the tournament abr ID (if there is one)"""
    # get all abr concluded tournaments that happened on that day
    json_filepath = Path('JSON/alwaysberunning.net/api/tournaments/' + date.isoformat() + '.json')
    if force or not json_filepath.is_file():
        date_string = date.strftime("%Y.%m.%d.")
        api_url = "https://alwaysberunning.net/api/tournaments"
        api_params = {
            'concluded':1,
            'start':date_string,
            'end':date_string
        }
        resp = requests.get(url=api_url, params=api_params)
        json_filepath.parent.mkdir(exist_ok=True, parents=True)
        with json_filepath.open(mode='w') as json_file:
            json.dump(resp.json(), json_file)
    with json_filepath.open(mode='r') as json_file:
        json_data = json.load(json_file)

    # look for a tournament with a matching name
    for tournament in json_data:
        if tournament['title'] == name:
            return tournament
    # look for a tournament with a matching size
    for tournament in json_data:
        if tournament['players_count'] == size:
            return tournament
    # or give up
    return {}

def get_abr_tournament_json(abr_id: int, force: bool = False) -> dict:
    """ get abr tournament json """
    json_filepath = Path('JSON/alwaysberunning.net/api/entries/' + str(abr_id) + '.json')
    if force or not json_filepath.is_file():
        api_url = "https://alwaysberunning.net/api/entries"
        api_params = {
            'id': abr_id
        }
        resp = requests.get(url=api_url, params=api_params)
        json_filepath.parent.mkdir(exist_ok=True, parents=True)
        with json_filepath.open(mode='w') as json_file:
            json.dump(resp.json(), json_file)
    with json_filepath.open(mode='r') as json_file:
        json_data = json.load(json_file)
    return json_data

def get_abr_player_mappings(json_data: dict) -> dict:
    """ use abr claims to match registration name to nrdb_id """
    player_map = {}
    json_filepath=Path('players.json')
    with json_filepath.open(mode='r') as players_file:
        known_players = json.load(players_file)
    for player in json_data:
        if player['user_id']:
            if str(player['user_id']) not in known_players:
                add_to_players_json(nrdb_id=int(player['user_id']), nrdb_name=player['user_name'])
            player_map.update( { player['user_import_name'] : player['user_id'] } )
    return player_map

def add_to_players_json(nrdb_id: int, nrdb_name: str):
    json_filepath=Path('players.json')
    with json_filepath.open(mode='r') as players_file:
        players = json.load(players_file)
    if nrdb_id not in players:
        print("found new nrdb_id: "+ nrdb_name + "["+str(nrdb_id)+"]")
        players[nrdb_id] = { 'nrdb_name': nrdb_name }
    with json_filepath.open(mode='w') as players_file:
        json.dump(players, players_file, indent=2)
 
def write_standings_to_csv(standings: list, standings_filepath: Path):
    standings_filepath.parent.mkdir(exist_ok=True, parents=True)
    with standings_filepath.open(mode='w',newline='') as sf:
        sw = csv.writer(sf, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
        sw.writerow(standings_header)
        sw.writerows(standings)

def write_tournament_results_to_csv(t: Tournament, results_filepath: Path):
    """ write tournament results to a CSV file """
    results_filepath.parent.mkdir(exist_ok=True, parents=True)
    with results_filepath.open(mode='w',newline='') as rf:
        rw = csv.writer(rf, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
        rw.writerow(results_header)
        for r in t.results:
            row = [ t.date, meta, t.region, online, tournament_id, t.name, r['phase'], r['round'], r['table'], r['corp_player'], r['corp_id'], r['result'], r['runner_player'], r['runner_id'] ]
            rw.writerow(row)                
    
def write_player_json_to_file(player: Player, filepath: Path):
    json_data = {'nrdb_id': player.nrdb_id, 'nrdb_name': player.nrdb_name, 'aliases': player.aliases, 'teams': player.teams, 'tournaments': player.tournaments}
    filepath.parent.mkdir(exist_ok=True, parents=True)
    with filepath.open(mode='w') as json_file:
        json.dump(json_data,json_file)

parser = argparse.ArgumentParser(description='get netrunner results from cobra, aesops and abr')
parser.add_argument('--cache-refresh', action=argparse.BooleanOptionalAction)
parser.set_defaults(cache_refresh=False)
parser.add_argument('--tournament', type=str)
args=parser.parse_args()

with open('tournaments.yml', 'r') as tournaments_file:
    config = yaml.safe_load(tournaments_file)

    standings_dir = 'OUTPUT/standings/'
    standings_header = ['date','region','online','tournament_id','tournament','top_cut_rank','swiss_rank','name','team 1','team 2','team 3','corp_name','corp_wins','corp_losses','corp_draws','runner_name','runner_wins','runner_losses','runner_draws','matchPoints','SoS','xSoS','corp_ID','corp_faction','runner_ID','runner_faction','nrdb_id']

    results_dir = 'OUTPUT/results/'
    results_header = [ 'date','meta','region','online','tournament_id','tournament','phase','round','table','corp_player','corp_id','result','runner_player','runner_id']

    player_dir = 'OUTPUT/players/'
    players = {}

    for meta,tournaments in config['meta'].items():
        if not tournaments:
            continue
        for tournament in tournaments:
            if 'alwaysberunning' in tournament['url']:
                tournament_abr_id = tournament['url'].split('/')[4] # https://alwaysberunning.net/tournaments/4241/uk-regionals-2024-east-anglia -> 4241
                tournament_name = tournament['url'].split('/')[5] # https://alwaysberunning.net/tournaments/4241/uk-regionals-2024-east-anglia -> uk-regional-2024-east-anglia
                print('['+meta+'] ' + tournament_name + ' [' + tournament['url'] + ']' )
                tournament_json = get_abr_tournament_json(tournament_abr_id, force=args.cache_refresh)
                tournament_date = tournament.get('date',None)
                tournament_size = len(tournament_json)
                tournament_level = tournament.get('level',None)
                tournament_online = tournament.get('online',False)
                tournament_region = tournament.get('region',None)
                tournament_player_map = tournament.get('players',{})
                get_abr_player_mappings(tournament_json) # using this method just to add any new players to players.json
                
                t = ABRTournament(name=tournament_name,json=tournament_json,date=tournament_date,region=tournament_region,online=tournament_online,player_mappings=tournament_player_map,abr_id=tournament_abr_id)
                tournament_id = "abr-" + tournament_abr_id
            else:
                tournament_json = get_json(tournament['url'], force=args.cache_refresh)
                tournament_name = tournament.get('name',tournament_json['name'])
                tournament_date = tournament.get('date',datetime.date.fromisoformat(tournament_json['date']))
                tournament_size = len(tournament_json['players'])
                print('['+meta+'] ' + tournament_name + ' [' + tournament['url'] + ']' )
                # try and get some details from abr
                tournament_abr = find_abr_tournament(date=tournament_date, name=tournament_name, size=tournament_size)
                tournament_abr_id = tournament.get('abr_id', tournament_abr.get('id',None))
                if not tournament_abr_id:
                    print("could not find tournament in abr (consider adding the abr_id to tournaments.yml)")
                tournament_level = tournament.get('level', tournament_abr.get('type',None))
                tournament_online = False
                if tournament.get('online',False) or (tournament_abr.get('location',None) == 'online'):
                    tournament_online = True
                # build a mapping of registration names to nrdb ids if possible
                tournament_player_map = {}
                if tournament_abr_id:
                    abr_tournament_json = get_abr_tournament_json(tournament_abr_id, force=args.cache_refresh)
                    tournament_player_map.update(get_abr_player_mappings(abr_tournament_json))
                tournament_player_map.update(tournament.get('players',{}))
                if 'aesop' in tournament['url']:
                    software = 'aesop'
                    t = AesopsTournament(name=tournament_name,json=tournament_json,date=tournament_date.isoformat(),region=tournament.get('region',None),online=tournament_online,player_mappings=tournament_player_map,abr_id=tournament_abr_id)
                else:
                    software = 'cobra'
                    t = CobraTournament(name=tournament_name,json=tournament_json,date=tournament_date.isoformat(),region=tournament.get('region',None),online=tournament_online,player_mappings=tournament_player_map, abr_id=tournament_abr_id)
                tournament_number = tournament['url'].rsplit('/', 1)[-1]
                tournament_id = software + '-' + tournament_number
            
            # useful variables
            if t.online is True:
                online = "netspace"
            else:
                online = "meatspace"
            
            # standings
            standings = t.standings
            for row in standings:
                row.insert(0,t.date)
                row.insert(1,t.region)
                row.insert(2,online)
                row.insert(3,tournament_id)
                row.insert(4,t.name)
            standings_filepath = Path(standings_dir + str(t.date) + '.' + tournament_id + '.standings.csv')
            write_standings_to_csv(standings=t.standings, standings_filepath=standings_filepath)
            
            results_filepath = Path(standings_dir + str(t.date) + '.' + tournament_id + '.results.csv')
            write_tournament_results_to_csv(t, results_filepath)
            
            # players
            for id,t_player in t.players.items():
                if t_player.nrdb_id:
                    if (type(t_player.nrdb_id)) != int:
                        print("WARNING! nrdb_id for "+t_player.name+"is "+type(t_player.nrdb_id)+" (expected int)")
                    if not players.get(t_player.nrdb_id):
                        players[t_player.nrdb_id] = Player(nrdb_id=t_player.nrdb_id)
                    players[t_player.nrdb_id].add_tournament_results(tournament_id=tournament_id, t_player=t_player, date=str(t.date), region=t.region, online=online, tournament_name=t.name, tournament_url=tournament['url'], tournament_level=tournament_level, meta=meta, abr_id=t.abr_id, size=len(t.players))
                else:
                    if t_player.cut_rank:
                        print("nrdb_id not found for "+t_player.name+" ["+str(t_player.cut_rank)+"]")

    for id,player in players.items():
        write_player_json_to_file(player=player, filepath=Path('OUTPUT/players/' + str(id) + '.json'))