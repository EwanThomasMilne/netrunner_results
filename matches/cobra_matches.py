import requests
from matches import TablesResultsByIdentity

class CobraTablesResultsByIdentity(TablesResultsByIdentity):

    def add_swiss_table_data(self, table, players):
        player1_runner = players.get_identity(player_id=table['player1']['id'], role='runner')
        player1_corp =  players.get_identity(player_id=table['player1']['id'], role='corp')
        player2_runner =  players.get_identity(player_id=table['player2']['id'], role='runner')
        player2_corp =  players.get_identity(player_id=table['player2']['id'], role='corp')

        phase = 'swiss'
        tableNum = table['table']

        # Game 1 of DSS
        result = 'unknown'        
        match table['player1']['runnerScore']: 
            case 3:
                result = 'runner'
            case 1:
                result = 'draw'
            case 0:
                result = 'corp'
        self.add_game_data(phase=phase, round='', table=tableNum, corp_player='', corp_id=player2_corp, winner=result, runner_player='', runner_id=player1_runner)

        # Game 2 of DSS
        result = 'unknown'
        match table['player1']['corpScore']:
            case 3:
                result = 'runner'
            case 1:
                result = 'draw'
            case 0:
                result = 'corp'
        self.add_game_data(phase=phase, round='', table=tableNum, corp_player='', corp_id=player1_corp, winner=result, runner_player='', runner_id=player2_runner)

    def add_cut_table_data(self, table, players):

        phase = 'cut'
        tableNum = table['table']
        result = 'unknown'

        # ever get the feeling that there must be a simpler way of doing something?
        if table['player1']['role'] == 'runner':
            runner_id = players.get_identity(table['player1']['id'], 'runner')
            corp_id = players.get_identity(table['player2']['id'], 'corp')
        else:
            runner_id = players.get_identity(table['player2']['id'], 'runner')
            corp_id = players.get_identity(table['player1']['id'], 'corp')
        
        if table['player1']['winner']:
            result = table['player1']['role']
        else:
            result = table['player2']['role']
            
        self.add_game_data(phase=phase, round='', table=tableNum, corp_player='', corp_id=corp_id, winner=result, runner_player='', runner_id=runner_id)
                        
    def add_table_data(self, table, players):
        if table['eliminationGame']:
            self.add_cut_table_data(table, players)
        else:
            self.add_swiss_table_data(table, players)



def get_json(url: str):
    # get the results from aesopstables.net from the URL of a given tournament
    json_url = url.strip() + '.json'
    resp = requests.get(url=json_url, params='')
    return resp.json()
