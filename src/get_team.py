import json
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description='find all members of a team')
parser.add_argument('teamname', type=str)
args=parser.parse_args()

json_filepath=Path('players.json',)
with json_filepath.open(mode='r') as json_file:
    players=json.load(json_file)
for nrdb_id,player in players.items():
    if args.teamname in player.get('teams', []):
        print("["+nrdb_id+"] "+player['nrdb_name'])