import requests
from winrate.winrate import ResultsByIdentityObject


class CobraResultsByIdentityObject(ResultsByIdentityObject):

    def add_swiss_table_data(self, table, players):
        player1runner = players.get_identity(player_id=table['player1']['id'], role='runner')
        player1corp =  players.get_identity(player_id=table['player1']['id'], role='corp')
        player2runner =  players.get_identity(player_id=table['player2']['id'], role='runner')
        player2corp =  players.get_identity(player_id=table['player2']['id'], role='corp')
        
        match table['player1']['runnerScore']: 
            case 3:
                self.add_result(player1runner, 'wins')
                self.add_result(player2corp, 'loses')
            case 1:
                self.add_result(player1runner, 'draws')
                self.add_result(player2corp, 'draws')
            case 0:
                self.add_result(player1runner, 'loses')
                self.add_result(player2corp, 'wins')
            
        match table['player1']['corpScore']:
            case 3:
                self.add_result(player1corp, 'wins')
                self.add_result(player2runner, 'loses')
            case 1:
                self.add_result(player1corp, 'draws')
                self.add_result(player2runner, 'draws')
            case 0:
                self.add_result(player1corp, 'loses')
                self.add_result(player2runner, 'wins')

    def add_cut_table_data(self, table, players):
        if table['player1']['winner']:
            winner = 'player1'
            loser = 'player2'
        else:
            winner = 'player2'
            loser = 'player2'
            
        self.add_result(players.get_identity(player_id=table[winner]['id'], role=table[winner]['role']), 'wins')
        self.add_result(players.get_identity(player_id=table[loser]['id'], role=table[loser]['role']), 'loses')

    def add_table_data(self, table, players):
        if table['eliminationGame']:
            self.add_cut_table_data(table, players)
        else:
            self.add_swiss_table_data(table, players)


def get_json(url: str):
    # get the results from tournaments.nullsignal.games from the URL of a given tournament
    json_url = url.strip() + '.json'
    resp = requests.get(url=json_url, params='')
    return resp.json()
