import requests
from winrate import ResultsByIdentityObject

class AesopsResultsByIdentityObject(ResultsByIdentityObject):

    def add_swiss_table_data(self, table, players):
        match table['runnerScore']:
            case '3':
                self.add_result(table['runnerIdentity'], 'wins')
                self.add_result(table['corpIdentity'], 'loses')
            case '1':
                self.add_result(table['runnerIdentity'], 'draws')
                self.add_result(table['corpIdentity'], 'draws')
            case '0':
                self.add_result(table['runnerIdentity'], 'loses')
                self.add_result(table['corpIdentity'], 'wins')

    def add_cut_table_data(self, table, players):
        if table['winner_id'] == table['runnerPlayer']:
            winner_role = 'runner'
            loser_role = 'corp'
        else:
            winner_role = 'corp'
            loser_role = 'runner'
            
        self.add_result(players.get_identity(player_id=table['winner_id'], role=winner_role), 'wins')
        self.add_result(players.get_identity(player_id=table['loser_id'], role=loser_role), 'loses')
                        
    def add_table_data(self, table, players):
        if table['runnerPlayer'] != '(BYE)' and table['corpPlayer'] != '(BYE)':
            if 'eliminationGame' in table: 
                self.add_cut_table_data(table, players)
            else:
                self.add_swiss_table_data(table, players)


def get_json(url: str):
    # get the results from aesopstables.net from the URL of a given tournament
    json_url = url.strip() + '/abr_export'
    resp = requests.get(url=json_url, params='')
    return resp.json()
