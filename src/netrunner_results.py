import csv
import yaml
from netrunner.tournament import AesopsTournament,CobraTournament

with open('config.yml', 'r') as configfile:
    config = yaml.safe_load(configfile)
    standings_dir = 'OUTPUT/standings/'
    standings_header = ['date','region','online','tournament','top_cut_rank','swiss_rank','name','corp_name','corp_wins','corp_losses','corp_draws','runner_name','runner_wins','runner_losses','runner_draws','matchPoints','SoS','xSoS','corp_ID','corp_faction','runner_ID','runner_faction']

    allstandings_filename = 'OUTPUT/allstandings.csv'
    with open (allstandings_filename,'w',newline='') as allstandings_file:
        allstandings_writer = csv.writer(allstandings_file, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
        allstandings_writer.writerow(standings_header)

        for tournament in config['tournaments']:
            if 'aesop' in tournament['url']:
                t = AesopsTournament(tournament['name'],tournament['url'],str(tournament['date']),tournament.get('online'))
            else:
                t = CobraTournament(tournament['name'],tournament['url'],str(tournament['date']),tournament.get('online'))                

            standings = t.standings
            for row in standings:
                row.insert(0,t.date)
                row.insert(1,t.region)
                if t.online is True:
                    row.insert(2,"netspace")
                else:
                    row.insert(2,"meatspace")
                row.insert(3,t.name)
                allstandings_writer.writerow(row)

            filename = standings_dir + str(tournament['date']) + '.' + tournament['name'] + '.standings.csv'
            with open(filename,'w',newline='') as f:
                w = csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
                w.writerow(standings_header)
                w.writerows(standings)