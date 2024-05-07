import cobra
import aesops
import csv

with open('config.txt') as config:
    for url in config:
        
        if 'aesop' in url:
            results = aesops.AesopsResults()
            json = aesops.get_aesops_json(url=url)
        else:
            results = cobra.CobraResults()
            json = cobra.get_cobra_json(url)

        results.tally_results(json['rounds'], json['players'])
        
        with open(json['name']+'.csv','w') as f:
            w = csv.writer(f)
            w.writerows(results.generate_report())