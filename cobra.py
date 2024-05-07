import requests
import generic as g


class CobraResults(g.Results):

    def tally_swiss_table(self, table, players):
        
        player1runner = players.get_identity(player_id=table['player1']['id'], role='runner')
        player1corp =  players.get_identity(player_id=table['player1']['id'], role='corp')
        player2runner =  players.get_identity(player_id=table['player2']['id'], role='runner')
        player2corp =  players.get_identity(player_id=table['player2']['id'], role='corp')
        
        match table['player1']['runnerScore']: 
            case 3:
                self.identities.add_result(player1runner, 'wins')
                self.identities.add_result(player2corp, 'loses')
            case 1:
                self.identities.add_result(player1runner, 'draws')
                self.identities.add_result(player2corp, 'draws')
            case 0:
                self.identities.add_result(player1runner, 'loses')
                self.identities.add_result(player2corp, 'wins')
            
        match table['player1']['corpScore']:
            case 3:
                self.identities.add_result(player1corp, 'wins')
                self.identities.add_result(player2runner, 'loses')
            case 1:
                self.identities.add_result(player1corp, 'draws')
                self.identities.add_result(player2runner, 'draws')
            case 0:
                self.identities.add_result(player1corp, 'loses')
                self.identities.add_result(player2runner, 'wins')

    def tally_cut_table(self, table, players):
        
        if table['player1']['winner']:
            winner = 'player1'
            loser = 'player2'
        else:
            winner = 'player2'
            loser = 'player2'
            
        self.identities.add_result(players.get_identity(player_id=table[winner]['id'], role=table[winner]['role']), 'wins')
        self.identities.add_result(players.get_identity(player_id=table[loser]['id'], role=table[loser]['role']), 'loses')

    def tally_results(self, rounds, players_dict):
        
        players = g.Players(players_dict)
        
        for round in rounds:
            for table in round:
                if table['eliminationGame']: 
                    self.tally_cut_table(table=table, players=players)
                else:
                    self.tally_swiss_table(table=table, players=players)


def get_cobra_json(url: str):
    # get the results from tournaments.nullsignal.games from the URL of a given tournament
    json_url = url.strip() + '.json'
    resp = requests.get(url=json_url, params='')
    return resp.json()
