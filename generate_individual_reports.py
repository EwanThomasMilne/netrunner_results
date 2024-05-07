import csv

import cobra
import aesops

from generic import PlayersWrapper

with open('config.txt') as config:
    for url in config:
        
        if 'aesop' in url:
            results = aesops.AesopsResultsByIdentityObject()
            json = aesops.get_json(url)
        else:
            results = cobra.CobraResultsByIdentityObject()
            json = cobra.get_json(url)

        results.add_tournament_data(json['rounds'], PlayersWrapper(json['players']))
        
        with open(json['name']+'.csv','w') as f:
            w = csv.writer(f)
            w.writerows(results.generate_report())