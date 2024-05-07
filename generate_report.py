import cobra
import aesops
import csv

#combined_results = ??

with open('config.txt') as config:
    for url in config:
        
        if 'aesop' in url:
            results = aesops.AesopsResults()
            json = aesops.get_aesops_json(url)
        else:
            results = cobra.CobraResults()
            json = cobra.get_cobra_json(url)

        results.tally_results(json['rounds'], json['players'])
        #combined_results.add_results(results)
        
    with open('results.csv','w') as f:
        w = csv.writer(f)
        w.writerows(combined_results.generate_report())