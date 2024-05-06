import cobra
import csv

url ='https://tournaments.nullsignal.games/tournaments/3419'

cobra_json = cobra.get_cobra_json(url)

results = cobra.tally_results(cobra_json['rounds'], cobra_json['players'])
        
with open(url[-4:]+'.csv','w') as f:
    w = csv.writer(f)
    w.writerows(results.items())