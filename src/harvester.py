import requests
import datetime
import csv
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

start_date = datetime.date(2024,1,1)
end_date = datetime.date(2024,9,12)
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

csv_filepath = Path('OUTPUT/nrdb_ids.csv')
csv_filepath.parent.mkdir(exist_ok=True, parents=True)
with csv_filepath.open(mode='w') as csv_file:
    csv_writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
    for name, id in nrdb_ids.items():
        csv_writer.writerow([name,id])