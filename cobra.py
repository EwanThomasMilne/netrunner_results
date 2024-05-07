import requests
import generic as g


class CobraResults(g.Results):

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
        
        players = g.Players(players_dict)
        
        for round in rounds:
            for match in round:
                if match['eliminationGame']: 
                    self.tally_cut_match(match=match, players=players)
                else:
                    self.tally_swiss_match(match=match, players=players)


def get_cobra_json(url: str):
    # get the results from tournaments.nullsignal.games from the URL of a given tournament
    json_url = url.strip() + '.json'
    resp = requests.get(url=json_url, params='')
    return resp.json()
