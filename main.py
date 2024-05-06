import cobra
import csv

results_by_identity = cobra.Results()

with open('config.txt') as config:
    for url in config:
        cobra_json = cobra.get_cobra_json(url)
        results_by_identity.tally_results(cobra_json['rounds'], cobra_json['players'])
        
        print(results_by_identity.identities.identities)
        
        # with open(cobra_json['name']+'.csv','w') as f:
        #     w = csv.writer(f)
        #     w.writerows(results.items())