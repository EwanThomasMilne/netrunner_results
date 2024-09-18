import requests
import datetime
import csv
import yaml
from pathlib import Path

def get_decklists_by_date(date: datetime.date):
    date_string = date.isoformat()
    json_url = "https://netrunnerdb.com/api/2.0/public/decklists/by_date/" + date_string
    resp = requests.get(url=json_url, params='')
    return resp.json()

def daterange(start_date: datetime.date, end_date: datetime.date):
    days = int((end_date - start_date).days)
    for n in range(days):
        yield start_date + datetime.timedelta(n)

def load_bre_csv()->dict:
    players = {}
    csv_filepath = Path('OUTPUT/sync_bre.csv')
    with csv_filepath.open(mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            try:
                nrdb_id = int(line[6])
                if nrdb_id not in players:
                    players[nrdb_id] = {}
                for alias in [line[0],line[1],line[2]]:
                    if alias != "":
                        if not players[nrdb_id].get('aliases'):
                            players[nrdb_id]['aliases'] = []
                        players[nrdb_id]['aliases'].append(alias)
                for team in [line[3],line[4],line[5]]:
                    if team != "":
                        if not players[nrdb_id].get('teams'):
                            players[nrdb_id]['teams'] = []
                        players[nrdb_id]['teams'].append(team)
            except ValueError:
                pass
    return players

start_date = datetime.date(2024,1,1)
end_date = datetime.date(2024,9,12)
players = load_bre_csv()
nrdb_ids = {}

for date in daterange(start_date, end_date):
#    date = datetime.date(2024, 1, 1)
    print(date)
    decklists_json = get_decklists_by_date(date)
#    print(decklists_json)
    for decklist in decklists_json.get('data'):
        username = decklist.get('user_name')
        userid = decklist.get('user_id')
        nrdb_ids.update({username:userid})
        if not players.get(userid):
            players[userid]={}
        players[userid].update({'nrdb_name': username})

csv_filepath = Path('OUTPUT/nrdb_ids.csv')
csv_filepath.parent.mkdir(exist_ok=True, parents=True)
with csv_filepath.open(mode='w') as csv_file:
    csv_writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
    for name, id in nrdb_ids.items():
        csv_writer.writerow([name,id])

yaml_filepath=Path('players.yml')
with yaml_filepath.open(mode='w') as players_file:
    yaml.dump(players, players_file)