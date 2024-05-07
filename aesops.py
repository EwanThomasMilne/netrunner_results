import requests
import generic as g 

class AesopsResults(g.Results):

    #TODO: remove unused argument from base class
    def tally_swiss_table(self, table, players):
        #TODO: why are these strings?
        match table['runnerScore']:
            case '3':
                self.identities.add_result(table['runnerIdentity'], 'wins')
                self.identities.add_result(table['corpIdentity'], 'loses')
            case '1':
                self.identities.add_result(table['runnerIdentity'], 'draws')
                self.identities.add_result(table['corpIdentity'], 'draws')
            case '0':
                self.identities.add_result(table['runnerIdentity'], 'loses')
                self.identities.add_result(table['corpIdentity'], 'wins')

    def tally_cut_table(self, table, players):
        if table['winner_id'] == table['runnerPlayer']:
            winner_role = 'runner'
            loser_role = 'corp'
        else:
            winner_role = 'corp'
            loser_role = 'runner'
            
        self.identities.add_result(players.get_identity(player_id=table['winner_id'], role=winner_role), 'wins')
        self.identities.add_result(players.get_identity(player_id=table['loser_id'], role=loser_role), 'loses')

    def tally_results(self, rounds, players_dict):
        players = g.Players(players_dict)
        
        for round in rounds:
            for table in round:
                if table['runnerPlayer'] != '(BYE)' and table['corpPlayer'] != '(BYE)':
                    if 'eliminationGame' in table: 
                        self.tally_cut_table(table=table, players=players)
                    else:
                        self.tally_swiss_table(table=table, players=players)


def get_aesops_json(url: str):
    # get the results from aesopstables.net from the URL of a given tournament
    json_url = url.strip() + '/abr_export'
    resp = requests.get(url=json_url, params='')
    return resp.json()
