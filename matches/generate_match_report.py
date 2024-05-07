import csv

import cobra_matches as cobra
import aesops_matches as aesops

from matches import TablesResultsByIdentity
from matches import PlayersWrapper

combined_results = TablesResultsByIdentity()

with open('config.txt') as config:
    for url in config:
        
        if 'aesop' in url:
            results = aesops.AesopsTablesResultsByIdentity()
            json = aesops.get_json(url)
        else:
            results = cobra.CobraTablesResultsByIdentity()
            json = cobra.get_json(url)

        results.add_tournament_data(json['rounds'], PlayersWrapper(json['players']))
        
        combined_results.add_results_object(results)
        
    with open('results.csv','w', newline='') as f:
        w = csv.writer(f)
        w.writerows(combined_results.generate_report())