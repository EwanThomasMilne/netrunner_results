import csv
import yaml

import cobra_matches as cobra
import aesops_matches as aesops

from matches import TablesResultsByIdentity
from matches import PlayersWrapper

combined_results = TablesResultsByIdentity()

with open('config.yml', 'r') as configfile:
    config = yaml.safe_load(configfile)

    for tournament in config['tournaments']:
        
        if 'aesop' in tournament['url']:
            results = aesops.AesopsTablesResultsByIdentity()
            json = aesops.get_json(tournament['url'])
        else:
            results = cobra.CobraTablesResultsByIdentity()
            json = cobra.get_json(tournament['url'])

        results.add_tournament_data(json['rounds'], PlayersWrapper(json['players']))
        
        combined_results.add_results_object(str(tournament['date']), tournament['name'], results)
        
    with open('results.csv','w', newline='') as f:
        w = csv.writer(f)
        w.writerows(combined_results.generate_report())