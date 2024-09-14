import requests
from matches import TablesResultsByIdentity

class AesopsTablesResultsByIdentity(TablesResultsByIdentity):


    def add_swiss_table_data(self, table, players, roundNum):
        phase = 'swiss'
        tableNum = table['tableNumber']
        runner_player = players.get_name(table['runnerPlayer'])
        corp_player = players.get_name(table['corpPlayer'])
        runner_id = players.get_identity(table['runnerPlayer'], 'runner')
        corp_id = players.get_identity(table['corpPlayer'], 'corp')
        
        result = 'unknown'
        match table['runnerScore']:
            case '3':
                result = 'runner'
            case '1':
                result = 'draw'
            case '0':
                result = 'corp'

        self.add_game_data(phase=phase, round=roundNum, table=tableNum, corp_player=corp_player, corp_id=corp_id, winner=result, runner_player=runner_player, runner_id=runner_id)

    def add_cut_table_data(self, table, players, roundNum):
        phase = 'cut'
        tableNum = table['tableNumber']
        runner_player = players.get_name(table['runnerPlayer'])
        corp_player = players.get_name(table['corpPlayer'])

        runner_id = players.get_identity(table['runnerPlayer'], 'runner')
        corp_id = players.get_identity(table['corpPlayer'], 'corp')
        
        if table['winner_id'] == table['runnerPlayer']:
            result = 'runner'
        else:
            result = 'corp'
            
        self.add_game_data(phase=phase, round=roundNum, table=tableNum, corp_player=corp_player, corp_id=corp_id, winner=result, runner_player=runner_player, runner_id=runner_id)       
                        
    def add_table_data(self, table, players, roundNum):

        if table['runnerPlayer'] != '(BYE)' and table['corpPlayer'] != '(BYE)':
            if 'eliminationGame' in table: 
                self.add_cut_table_data(table, players, roundNum)
            else:
                self.add_swiss_table_data(table, players, roundNum)


def get_json(url: str):
    # get the results from aesopstables.net from the URL of a given tournament
    json_url = url.strip() + '/abr_export'
    resp = requests.get(url=json_url, params='')
    return resp.json()
