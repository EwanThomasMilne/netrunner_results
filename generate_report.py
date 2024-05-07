import csv

import cobra
import aesops

from generic import ResultsByIdentityObject
from generic import PlayersWrapper

combined_results = ResultsByIdentityObject()

with open('config.txt') as config:
    for url in config:
        
        if 'aesop' in url:
            results = aesops.AesopsResultsByIdentityObject()
            json = aesops.get_json(url)
        else:
            results = cobra.CobraResultsByIdentityObject()
            json = cobra.get_json(url)

        results.add_tournament_data(json['rounds'], PlayersWrapper(json['players']))
        
        combined_results.add_results_object(results)
        
    with open('results.csv','w', newline='') as f:
        w = csv.writer(f)
        w.writerows(combined_results.generate_report())