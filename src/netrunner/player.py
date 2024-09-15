import csv
from netrunner.identity import Identity

def determine_nrdb_id(name: str) -> int:
    # expect csv to be in the format ["nrdb_name","nrdb_id"]
    with open('OUTPUT/nrdb_ids.csv', newline='') as f:
        reader = csv.reader(f)
        for line in reader:
            if line[0] == name:
                return line[1]
    return ''

class TournamentPlayer:
    """
    A class representing a netrunner player at a tournament
    
    Attributes:
        name (str): the name under which the player registered for the tournament
        tournament_id (int): tournament id number of player
        nrdb_id (int): nrdb id number of player
        corp_id (netrunner.identity): corp identity
        runner_id (netrunner.identity): runner identity
        corp_wins (int): number of wins when playing as corp
        corp_losses (int): number of losses when playing as corp
        corp_draws (int): number of draws when playing as corp
        runner_wins (int): number of wins when playing as runner
        runner_losses (int): number of losses when playing as runner
        runner_draws (int): number of draws when playing as runner
        swiss_rank (int): final position after swiss
        cut_rank (int): final position after top cut
        match_points (int): match points accrued in swiss
        SoS (float): strength of schedule
        xSoS (float): extended strength of schedule
        side_balance (int): how many more corp games has the player played than runner (a negative value means a runner bias)
    """
    def __init__(self, tournament_id: int, name: str, corp_id: Identity, runner_id: Identity, swiss_rank: int, match_points: int, SoS: float, xSoS: float, side_balance: int = 0, cut_rank: int = ''):
        self.tournament_id = tournament_id
        self.name = name
        self.nrdb_id = determine_nrdb_id(self.name)
        self.corp_id = corp_id
        self.runner_id = runner_id
        self.corp_wins = 0
        self.corp_losses = 0
        self.corp_draws = 0
        self.runner_wins = 0
        self.runner_losses = 0
        self.runner_draws = 0
        self.swiss_rank = swiss_rank
        self.cut_rank = cut_rank
        self.match_points = match_points
        self.SoS = SoS
        self.xSoS = xSoS
        self.side_balance = side_balance

    def record_corp_result(self, game_data: dict):
        match game_data['result']:
            case 'corp':
                self.corp_wins += 1
            case 'runner':
                self.corp_losses += 1
            case 'draw':
                self.corp_draws += 1

    def record_runner_result(self, game_data: dict):
        match game_data['result']:
            case 'runner':
                self.runner_wins += 1
            case 'corp':
                self.runner_losses += 1
            case 'draw':
                self.runner_draws += 1