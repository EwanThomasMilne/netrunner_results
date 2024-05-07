import csv

import cobra_winrate as cobra
import aesops_winrate as aesops

from winrate.winrate import PlayersWrapper

with open('config.txt') as config:
    for url in config:
        
        if 'aesop' in url:
            results = aesops.AesopsResultsByIdentityObject()
            json = aesops.get_json(url)
        else:
            results = cobra.CobraResultsByIdentityObject()
            json = cobra.get_json(url)

        results.add_tournament_data(json['rounds'], PlayersWrapper(json['players']))
        
        with open(json['name']+'.csv','w', newline='') as f:
            w = csv.writer(f)
            w.writerows(results.generate_report())