import requests
from matches import TablesResultsByIdentity

class AesopsTablesResultsByIdentity(TablesResultsByIdentity):


    def add_swiss_table_data(self, table, players):
        
        runner_id = players.get_identity(table['runnerPlayer'], 'runner')
        corp_id = players.get_identity(table['corpPlayer'], 'corp')
        
        match table['runnerScore']:
            case '3':
                self.add_game_data(runner_id=runner_id, corp_id=corp_id, winner='runner', draw=False)

            case '1':
                self.add_game_data(runner_id=runner_id, corp_id=corp_id, winner='', draw=True)

            case '0':
                self.add_game_data(runner_id=runner_id, corp_id=corp_id, winner='corp', draw=False)

    def add_cut_table_data(self, table, players):
        
        runner_id = players.get_identity(table['runnerPlayer'], 'runner')
        corp_id = players.get_identity(table['corpPlayer'], 'corp')
        
        if table['winner_id'] == table['runnerPlayer']:
            winner = 'runner'
        else:
            winner = 'corp'
            
        self.add_game_data(runner_id=runner_id, corp_id=corp_id, winner=winner, draw=False)
        
                        
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
