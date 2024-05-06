import requests

#TODO: think up some better class names

class Players:

    def __init__(self, player_dict) -> None:
        self.player_dict = player_dict
        
    # takes a player's cobra id and a side and returns their id for that side
    def get_identity(self, player_id: int, role: str) -> str:
        for player in self.player_dict:
            if player['id'] == player_id:
                return player[role+'Identity']


class Identities:
    
    def __init__(self) -> None:
            
        self.identities = {}
        
    #TODO: move the for loop into the results class somehow
    def generate_rows(self):
        for identity, values in self.identities.items():
            yield [identity, values["wins"], values["draws"], values["loses"]] 
            
    def add_result(self, identity: str, result: str):
        
        if identity not in self.identities:
            self.identities.update({identity: {'wins': 0, 'draws': 0, 'loses': 0}})
            
        self.identities[identity][result] += 1


class Results:
    
    def __init__(self) -> None:
        self.identities = Identities()
        
    def generate_report(self):
        
        result = [['id','wins','draws','loses']]
        for row in self.identities.generate_rows():
            result.append(row)
            
        return result

    def tally_swiss_match(self, match, players):
        
        player1runner = players.get_identity(player_id=match['player1']['id'], role='runner')
        player1corp =  players.get_identity(player_id=match['player1']['id'], role='corp')
        player2runner =  players.get_identity(player_id=match['player2']['id'], role='runner')
        player2corp =  players.get_identity(player_id=match['player2']['id'], role='corp')
        
        #player 1 wins thier runner game
        if match['player1']['runnerScore'] == 3:
            self.identities.add_result(player1runner, 'wins')
            self.identities.add_result(player2corp, 'loses')
        # draw
        elif match['player1']['runnerScore'] == 1:
            self.identities.add_result(player1runner, 'draws')
            self.identities.add_result(player2corp, 'draws')
        #player 1 loses thier runner game
        elif match['player1']['runnerScore'] == 0:
            self.identities.add_result(player1runner, 'loses')
            self.identities.add_result(player2corp, 'wins')
            
        #player 1 wins thier corp game
        if match['player1']['corpScore'] == 3:
            self.identities.add_result(player1corp, 'wins')
            self.identities.add_result(player2runner, 'loses')
        # draw
        elif match['player1']['corpScore'] == 1:
            self.identities.add_result(player1corp, 'draws')
            self.identities.add_result(player2runner, 'draws')
        #player 1 loses thier corp game
        elif match['player1']['corpScore'] == 0:
            self.identities.add_result(player1corp, 'loses')
            self.identities.add_result(player2runner, 'wins')

    def tally_cut_match(self, match, players):
        
        if match['player1']['winner']:
            winner = 'player1'
            loser = 'player2'
        else:
            winner = 'player2'
            loser = 'player2'
            
        self.identities.add_result(players.get_identity(player_id=match[winner]['id'], role=match[winner]['role']), 'wins')
        self.identities.add_result(players.get_identity(player_id=match[loser]['id'], role=match[loser]['role']), 'loses')

    def tally_results(self, rounds, players_dict):
        
        players = Players(players_dict)
        
        for round in rounds:
            for match in round:
                if match['eliminationGame']: 
                    self.tally_cut_match(match=match, players=players)
                else:
                    self.tally_swiss_match(match=match, players=players)


def get_cobra_json(url: str):
    # get the results from cobra from a URL of a given tournament
    resp = requests.get(url=url+'.json', params='')
    return resp.json()
