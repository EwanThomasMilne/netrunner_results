import cobra
import aesops
import csv

with open('config.txt') as config:
    for url in config:
        
        if 'aesop' in url:
            results_by_identity = aesops.AesopsResults()
            json = aesops.get_aesops_json(url=url)
        else:
            results_by_identity = cobra.CobraResults()
            json = cobra.get_cobra_json(url)

        results_by_identity.tally_results(json['rounds'], json['players'])
        
        for row in results_by_identity.generate_report():
            print(row)
        
        with open(json['name']+'.csv','w') as f:
            w = csv.writer(f)
            w.writerows(results_by_identity.generate_report())