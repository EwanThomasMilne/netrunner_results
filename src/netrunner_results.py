import csv
import yaml
import requests
import json
import datetime
from pathlib import Path
from netrunner.tournament import AesopsTournament,CobraTournament
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
    
def get_abr_tournament_id(date: datetime.date, name: str, size: int) -> int:
    """ use the abr API to find the tournament abr ID (if there is one)"""
    # get all abr concluded tournaments that happened on that day
    date_string = date.strftime("%Y.%m.%d.")
    api_url = "https://alwaysberunning.net/api/tournaments"
    api_params = {
        'concluded':1,
        'start':date_string,
        'end':date_string
    }
    resp = requests.get(url=api_url, params=api_params)

    # look for a tournament with a matching name
    for tournament in resp.json():
        if tournament['title'] == name:
            return tournament['id']
        
    # look for a tournament with a matching size
    for tournament in resp.json():
        if tournament['players_count'] == size:
            return tournament['id']
        
    # or give up
    print("could not find tournament in abr (consider adding the abr_id to tournaments.yml)")
    return None
 
def write_standings_to_csv(standings: list, standings_filepath: Path):
    standings_filepath.parent.mkdir(exist_ok=True, parents=True)
    with standings_filepath.open(mode='w',newline='') as sf:
        sw = csv.writer(sf, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
        sw.writerow(standings_header)
        sw.writerows(standings)

    
def write_player_json_to_file(player: Player, filepath: Path):
    json_data = {'nrdb_id': player.nrdb_id, 'nrdb_name': player.nrdb_name, 'aliases': player.aliases, 'teams': player.teams, 'tournaments': player.tournaments}
    filepath.parent.mkdir(exist_ok=True, parents=True)
    with filepath.open(mode='w') as json_file:
        json.dump(json_data,json_file)

with open('tournaments.yml', 'r') as tournaments_file:
    config = yaml.safe_load(tournaments_file)

    standings_dir = 'OUTPUT/standings/'
    standings_header = ['date','region','online','tournament_id','tournament','top_cut_rank','swiss_rank','name','team 1','team 2','team 3','corp_name','corp_wins','corp_losses','corp_draws','runner_name','runner_wins','runner_losses','runner_draws','matchPoints','SoS','xSoS','corp_ID','corp_faction','runner_ID','runner_faction','nrdb_id']
    allstandings_filepath = Path('OUTPUT/allstandings.csv')
    allstandings_filepath.parent.mkdir(exist_ok=True, parents=True)

    results_dir = 'OUTPUT/results/'
    results_header = [ 'date','meta','region','online','tournament_id','tournament','phase','round','table','corp_player','corp_id','result','runner_player','runner_id']
    allresults_filepath = Path('OUTPUT/allresults.csv')
    allresults_filepath.parent.mkdir(exist_ok=True, parents=True)

    player_dir = 'OUTPUT/players/'
    players = {}

    with allstandings_filepath.open(mode='w',newline='') as allstandings_file, allresults_filepath.open(mode='w',newline='') as allresults_file:
        allstandings_writer = csv.writer(allstandings_file, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
        allstandings_writer.writerow(standings_header)

        allresults_writer = csv.writer(allresults_file, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
        allresults_writer.writerow(results_header)

        for meta,tournaments in config['meta'].items():
            print('META: ' + meta)
            if not tournaments:
                continue
            for tournament in tournaments:
                tournament_json = get_json(tournament['url'])
                tournament_name = tournament.get('name',tournament_json['name'])
                tournament_date = tournament.get('date',datetime.date.fromisoformat(tournament_json['date']))
                tournament_size = len(tournament_json['players'])
                print('TOURNAMENT: ' + tournament_name + ' [' + tournament['url'] + ']' )
                tournament_abr_id = tournament.get('abr_id', get_abr_tournament_id(date=tournament_date, name=tournament_name, size=tournament_size))

                if 'aesop' in tournament['url']:
                    software = 'aesop'
                    t = AesopsTournament(name=tournament_name,json=tournament_json,date=tournament_date.isoformat(),region=tournament.get('region',None),online=tournament.get('online',False),player_mappings=tournament.get('players',None),abr_id=tournament_abr_id)
                else:
                    software = 'cobra'
                    t = CobraTournament(name=tournament_name,json=tournament_json,date=tournament_date.isoformat(),region=tournament.get('region',None),online=tournament.get('online',False),player_mappings=tournament.get('players',None), abr_id=tournament_abr_id)
                
                # useful variables
                if t.online is True:
                    online = "netspace"
                else:
                    online = "meatspace"
                tournament_number = tournament['url'].rsplit('/', 1)[-1]
                tournament_id = software + '-' + tournament_number

                # standings
                standings = t.standings
                for row in standings:
                    row.insert(0,t.date)
                    row.insert(1,t.region)
                    row.insert(2,online)
                    row.insert(3,tournament_id)
                    row.insert(4,t.name)
                    allstandings_writer.writerow(row)

                standings_filepath = Path(standings_dir + str(t.date) + '.' + tournament_id + '.standings.csv')
                write_standings_to_csv(standings=t.standings, standings_filepath=standings_filepath)

                # results
                results = t.results
                results_filename = results_dir + str(t.date) + '.' + tournament_id + '.results.csv'
                with open(results_filename,'w',newline='') as rf:
                    rw = csv.writer(rf, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
                    rw.writerow(results_header)
                    for r in results:
                        row = [ t.date, meta, t.region, online, tournament_id, t.name, r['phase'], r['round'], r['table'], r['corp_player'], r['corp_id'], r['result'], r['runner_player'], r['runner_id'] ]
                        allresults_writer.writerow(row)
                        rw.writerow(row)

                # players
                for id,t_player in t.players.items():
                    if t_player.nrdb_id:
                        if not players.get(t_player.nrdb_id):
                            players[t_player.nrdb_id] = Player(nrdb_id=t_player.nrdb_id)
                        players[t_player.nrdb_id].add_tournament_results(tournament_id=tournament_id, t_player=t_player, date=str(t.date), region=t.region, online=online, tournament_name=t.name, tournament_url=tournament['url'], tournament_level=tournament.get('level',None), meta=meta, abr_id=t.abr_id, size=len(t.players))

    for id,player in players.items():
        write_player_json_to_file(player=player, filepath=Path('OUTPUT/players/' + str(id) + '.json'))