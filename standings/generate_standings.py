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
        standings.append(standing)
    return standings

with open('config.yml', 'r') as configfile:
    config = yaml.safe_load(configfile)

    for tournament in config['tournaments']:

        if 'aesop' in tournament['url']:
            sys.exit('generate standings from aesops is not implemented')
        else:
            filename = tournament['name'] + '.standings.csv'
            json = get_cobra_json(tournament['url'])
            standings = return_cobra_standings(json)

        with open(filename,'w',newline='') as f:
            w = csv.writer(f)
            w.writerows(standings)

