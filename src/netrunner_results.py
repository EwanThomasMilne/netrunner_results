import csv
import yaml
from netrunner.tournament import AesopsTournament,CobraTournament
from netrunner.player import TournamentPlayer

with open('config.yml', 'r') as configfile:
    config = yaml.safe_load(configfile)

    standings_dir = 'OUTPUT/standings/'
    standings_header = ['date','region','online','tournament','top_cut_rank','swiss_rank','name','team 1','team 2','team 3','corp_name','corp_wins','corp_losses','corp_draws','runner_name','runner_wins','runner_losses','runner_draws','matchPoints','SoS','xSoS','corp_ID','corp_faction','runner_ID','runner_faction','nrdb_id']
    allstandings_filename = 'OUTPUT/allstandings.csv'

    results_dir = 'OUTPUT/results/'
    results_header = [ 'date','meta','region','online','software','tournament','phase','round','table','corp_player','corp_id','result','runner_player','runner_id']
    allresults_filename = 'OUTPUT/allresults.csv'

    player_dir = 'OUTPUT/players/'

    with open(allstandings_filename,'w',newline='') as allstandings_file, open(allresults_filename,'w',newline='') as allresults_file:
        allstandings_writer = csv.writer(allstandings_file, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
        allstandings_writer.writerow(standings_header)

        allresults_writer = csv.writer(allresults_file, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
        allresults_writer.writerow(results_header)

        for meta,tournaments in config['meta'].items():
            print('META: ' + meta)
            for tournament in tournaments:
                if 'aesop' in tournament['url']:
                    software = 'aesops'
                    t = AesopsTournament(name=tournament.get('name',None),url=tournament['url'],date=tournament.get('date',None),region=tournament.get('region',None),online=tournament.get('online',False))
                else:
                    software = 'cobra'
                    t = CobraTournament(name=tournament.get('name',None),url=tournament['url'],date=tournament.get('date',None),region=tournament.get('region',None),online=tournament.get('online',False))
                print('TOURNAMENT: ' + t.name + ' [' + tournament['url'] + ']' )

                if t.online is True:
                    online = "netspace"
                else:
                    online = "meatspace"

                standings = t.standings
                for row in standings:
                    row.insert(0,t.date)
                    row.insert(1,t.region)
                    row.insert(2,online)
                    row.insert(3,t.name)
                    allstandings_writer.writerow(row)

                standings_filename = standings_dir + str(t.date) + '.' + t.name + '.standings.csv'
                with open(standings_filename,'w',newline='') as sf:
                    sw = csv.writer(sf, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
                    sw.writerow(standings_header)
                    sw.writerows(standings)

                results = t.results
                results_filename = results_dir + str(t.date) + '.' + t.name + '.results.csv'
                with open(results_filename,'w',newline='') as rf:
                    rw = csv.writer(rf, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
                    rw.writerow(results_header)
                    for r in results:
                        row = [ t.date, meta, t.region, online, software, t.name, r['phase'], r['round'], r['table'], r['corp_player'], r['corp_id'], r['result'], r['runner_player'], r['runner_id'] ]
                        allresults_writer.writerow(row)
                        rw.writerow(row)

                players = t.players
                for id,player in players.items():
                    if player.nrdb_id:
                        player_results_filename = player_dir + str(player.nrdb_id) + '.results.csv'
                        with open(player_results_filename,'a',newline='') as prf:
                            prw = csv.writer(prf, quotechar='"', quoting=csv.QUOTE_ALL, escapechar='\\')
                            for r in player.results:
                                row = [ t.date, meta, t.region, online, software, t.name, r['phase'], r['round'], r['table'], r['corp_player'], r['corp_id'], r['result'], r['runner_player'], r['runner_id'] ]
                                prw.writerow(row)