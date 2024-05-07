import cobra
import csv

results_by_identity = cobra.Results()

with open('config.txt') as config:
    for url in config:
        
        if 'aesop' in url:
            json = cobra.get_aesops_json(url)
        else:
            json = cobra.get_cobra_json(url)

        results_by_identity.tally_results(json['rounds'], json['players'])
        
        for row in results_by_identity.generate_report():
            print(row)
        
        with open('results.csv','w') as f:
            w = csv.writer(f)
            w.writerows(results_by_identity.generate_report())