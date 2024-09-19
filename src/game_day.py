import requests

min_players = 16

for id in range(1,4000):
    tournament_url = 'https://tournaments.nullsignal.games/tournaments/'+str(id)+'.json'    
#    tournament_url = 'https://www.aesopstables.net/'+str(id)+'.json'
    try:
        tournament_data = requests.get(url=tournament_url, params='').json()
    except Exception:
        continue
    if 'players' in tournament_data and len(tournament_data['players']) >= min_players:
        if 'eliminationPlayers' in tournament_data and tournament_data['eliminationPlayers']:
            print(tournament_url+' ['+tournament_data['date']+'] - '+tournament_data['name'])