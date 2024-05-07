import requests
import generic as g 

class AesopsResults(g.Results):

    #TODO: remove unused argument from base class
    def tally_swiss_match(self, match, players):
        
        #TODO: convert to a switch statement
        if match['runnerScore'] == '3':
            self.identities.add_result(match['runnerIdentity'], 'wins')
            self.identities.add_result(match['corpIdentity'], 'loses')
        elif match['runnerScore'] == '1':
            self.identities.add_result(match['runnerIdentity'], 'draws')
            self.identities.add_result(match['corpIdentity'], 'draws')
        elif match['runnerScore'] == '0':
            self.identities.add_result(match['runnerIdentity'], 'loses')
            self.identities.add_result(match['corpIdentity'], 'wins')

    def tally_cut_match(self, match, players):
        
        if match['winner_id'] == match['runnerPlayer']:
            winner_role = 'runner'
            loser_role = 'corp'
        else:
            winner_role = 'corp'
            loser_role = 'runner'
            
        self.identities.add_result(players.get_identity(player_id=match['winner_id'], role=winner_role), 'wins')
        self.identities.add_result(players.get_identity(player_id=match['loser_id'], role=loser_role), 'loses')

    def tally_results(self, rounds, players_dict):
        
        players = g.Players(players_dict)
        
        for round in rounds:
            for match in round:
                if match['runnerPlayer'] != '(BYE)' and match['corpPlayer'] != '(BYE)':
                    if 'eliminationGame' in match: 
                        self.tally_cut_match(match=match, players=players)
                    else:
                        self.tally_swiss_match(match=match, players=players)

def get_aesops_json(url: str):
    # get the results from aesopstables.net from the URL of a given tournament
    json_url = url.strip() + '/abr_export'
    resp = requests.get(url=json_url, params='')
    return resp.json()