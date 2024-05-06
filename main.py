import cobra
import csv

with open('config.txt') as config:
    for url in config:
        cobra_json = cobra.get_cobra_json(url)
        results = cobra.tally_results(cobra_json['rounds'], cobra_json['players'])
        
        with open(cobra_json['name']+'.csv','w') as f:
            w = csv.writer(f)
            w.writerows(results.items())