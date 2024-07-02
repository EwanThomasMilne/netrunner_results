class PlayersWrapper:
    #provides methods for searching the players dictionary

    def __init__(self, player_dict) -> None:
        self.player_dict = player_dict
        
    # takes a player's cobra id and a side and returns their id for that side
    def get_identity(self, player_id: int, role: str) -> str:
        for player in self.player_dict:
            if player['id'] == player_id:
                return player[role+'Identity']

    # takes a player's cobra id and returns their name
    def get_name(self, player_id: int) -> str:
        for player in self.player_dict:
            if player['id'] == player_id:
                return player['name']


class TablesResultsByIdentity:
    #takes in tournament data and sorts it by identity rather than round
    
    def __init__(self) -> None:
        self.games = []
        
    def add_results_object(self, results_object):
        # takes another ResultsByIdentityObject and adds those results to this object
        for result in results_object.games:
            self.games.append(result)
        
    def add_game_data(self, phase, round, table, corp_player, corp_id, winner, runner_player, runner_id):
        self.games.append({ 'phase': phase, 'round': round, 'table': table, 'corp_player': corp_player, 'corp_id': corp_id, 'winner': winner, 'runner_player': runner_player, 'runner_id': runner_id })

    def add_table_data(self, table, players):
        pass
        
    def add_round_data(self, round, players, roundNum):
        # takes a dictionary of data about a round and adds it to the identities_dict
        for table in round:
            self.add_table_data(table, players, roundNum)
        
    def add_tournament_data(self, tournament, players):
        # takes a dictionary of data about mutliple rounds in a tournament and adds it to the identities_dict
        roundNum = 1
        for round in tournament:
            self.add_round_data(round, players, roundNum)
            roundNum += 1

    
    def generate_report(self):
        # generates a flat view of the results suitable for printing or outputting
        report = [[ 'phase', 'round', 'table', 'corp_player', 'corp_id', 'result', 'runner_player', 'runner_id' ]]
        
        for game in self.games:
            report.append([game['phase'], game['round'], game['table'], game['corp_player'], game['corp_id'], game['winner'], game['runner_player'], game['runner_id']])
        
        return report
