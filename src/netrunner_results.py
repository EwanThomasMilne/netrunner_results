import csv
import yaml
import requests
import json
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

    results_dir = 'OUTPUT/results/'
    results_header = [ 'date','meta','region','online','tournament_id','tournament','phase','round','table','corp_player','corp_id','result','runner_player','runner_id']
    allresults_filepath = Path('OUTPUT/allresults.csv')

    player_dir = 'OUTPUT/players/'
    players = {}

    allstandings_filepath.parent.mkdir(exist_ok=True, parents=True)
    allresults_filepath.parent.mkdir(exist_ok=True, parents=True)
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
                if 'aesop' in tournament['url']:
                    software = 'aesop'
                    t = AesopsTournament(name=tournament.get('name',None),json=tournament_json,date=tournament.get('date',None),region=tournament.get('region',None),online=tournament.get('online',False),player_mappings=tournament.get('players',None))
                else:
                    software = 'cobra'
                    t = CobraTournament(name=tournament.get('name',None),json=tournament_json,date=tournament.get('date',None),region=tournament.get('region',None),online=tournament.get('online',False),player_mappings=tournament.get('players',None))
                print('TOURNAMENT: ' + t.name + ' [' + tournament['url'] + ']' )

                if t.online is True:
                    online = "netspace"
                else:
                    online = "meatspace"

                tournament_number = tournament['url'].rsplit('/', 1)[-1]
                tournament_id = software + '-' + tournament_number

                standings = t.standings
                for row in standings:
                    row.insert(0,t.date)
                    row.insert(1,t.region)
                    row.insert(2,online)
                    row.insert(3,tournament_id)
                    row.insert(4,t.name)
                    allstandings_writer.writerow(row)

                standings_filepath = Path(standings_dir + str(t.date) + '.' + tournament_id + '.standings.csv')
                standings_filepath.parent.mkdir(exist_ok=True, parents=True)
                with standings_filepath.open(mode='w',newline='') as sf:
                    sw = csv.writer(sf, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
                    sw.writerow(standings_header)
                    sw.writerows(standings)

                results = t.results
                results_filename = results_dir + str(t.date) + '.' + tournament_id + '.results.csv'
                with open(results_filename,'w',newline='') as rf:
                    rw = csv.writer(rf, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
                    rw.writerow(results_header)
                    for r in results:
                        row = [ t.date, meta, t.region, online, tournament_id, t.name, r['phase'], r['round'], r['table'], r['corp_player'], r['corp_id'], r['result'], r['runner_player'], r['runner_id'] ]
                        allresults_writer.writerow(row)
                        rw.writerow(row)

                for id,t_player in t.players.items():
                    if t_player.nrdb_id:
                        if not players.get(t_player.nrdb_id):
                            players[t_player.nrdb_id] = Player(nrdb_id=t_player.nrdb_id)
                        players[t_player.nrdb_id].add_tournament_results(tournament_id=tournament_id, t_player=t_player, date=str(t.date), region=t.region, online=online, tournament_name=t.name, tournament_url=tournament['url'], tournament_level=tournament.get('level',None), meta=meta, size=len(t.players))

    for id,player in players.items():
        write_player_json_to_file(player=player, filepath=Path('OUTPUT/players/' + str(id) + '.json'))