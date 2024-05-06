import requests

class Players:

    def __init__(self, player_dict) -> None:
        self.player_dict = player_dict
        
    # takes a player's cobra id and a side and returns their id for that side
    def get_identity(self, player_id: int, role: str) -> str:
        for player in self.player_dict:
            if player['id'] == player_id:
                return player[role+'Identity']

def get_cobra_json(url: str):
    # get the results from cobra from a URL of a given tournament
    resp = requests.get(url=url+'.json', params='')
    return resp.json()

def create_id_list(players):
    #create a dictionary of all IDs played
    id_list = {}
    for player in players:
        id_list.update({player['runnerIdentity']: {'wins': 0, 'draws': 0, 'loses': 0}})
        id_list.update({player['corpIdentity']: {'wins': 0, 'draws': 0, 'loses': 0}})
        
    return id_list

def tally_swiss_match(match, players, id_list):
        
    player1runner = players.get_identity(player_id=match['player1']['id'], role='runner')
    player1corp =  players.get_identity(player_id=match['player1']['id'], role='corp')
    player2runner =  players.get_identity(player_id=match['player2']['id'], role='runner')
    player2corp =  players.get_identity(player_id=match['player2']['id'], role='corp')
    
    #player 1 wins thier runner game
    if match['player1']['runnerScore'] == 3:
        id_list[player1runner]['wins'] += 1
        id_list[player2corp]['loses'] += 1
    # draw
    elif match['player1']['runnerScore'] == 1:
        id_list[player1runner]['draws'] += 1
        id_list[player2corp]['draws'] += 1
    #player 1 loses thier runner game
    elif match['player1']['runnerScore'] == 0:
        id_list[player1runner]['loses'] += 1
        id_list[player2corp]['wins'] += 1
    else:
        print("error")
        
    #player 1 wins thier corp game
    if match['player1']['corpScore'] == 3:
        id_list[player1corp]['wins'] += 1
        id_list[player2runner]['loses'] += 1
    # draw
    elif match['player1']['corpScore'] == 1:
        id_list[player1corp]['draws'] += 1
        id_list[player2runner]['draws'] += 1
    #player 1 loses thier corp game
    elif match['player1']['corpScore'] == 0:
        id_list[player1corp]['loses'] += 1
        id_list[player2runner]['wins'] += 1
    else:
        print("error")

def tally_cut_match(match, players, id_list):
    
    if match['player1']['winner']:
        winner = 'player1'
        loser = 'player2'
    else:
        winner = 'player2'
        loser = 'player2'
        
    id_list[players.get_identity(player_id=match[winner]['id'], role=match[winner]['role'])]['wins'] += 1
    id_list[players.get_identity(player_id=match[loser]['id'], role=match[loser]['role'])]['loses'] += 1


def tally_results(rounds, players_dict):
    
    players = Players(players_dict)
    id_list = create_id_list(players_dict)
    
    for round in rounds:
        for match in round:
            if match['eliminationGame']: 
                tally_cut_match(match=match, players=players, id_list=id_list)
            else:
                tally_swiss_match(match=match, players=players, id_list=id_list)

    return id_list
    