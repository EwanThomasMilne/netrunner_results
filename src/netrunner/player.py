import csv
from netrunner.identity import Identity

def determine_nrdb_id(name: str) -> int:
    nrdb_id = None
    try:
        nrdb_id = determine_nrdb_id_from_csv(name)
    except:
        pass
    if nrdb_id:
        return nrdb_id
    try:
        nrdb_id = determine_nrdb_id_from_bre(name)
    except:
        pass
    if nrdb_id:
        return nrdb_id
    return None

def determine_nrdb_id_from_csv(name: str) -> int:
    # expect csv to be in the format ["nrdb_name","nrdb_id"]
    with open('OUTPUT/nrdb_ids.csv', newline='') as f:
        reader = csv.reader(f)
        for line in reader:
            if line[0].lower() == name.lower():
                try:
                    return int(line[1])
                except ValueError:
                    return None
    return None

def determine_nrdb_id_from_bre(name: str) -> int:
    # expect csv to be in the format ["player name","player alias","player alias 2","testing team","team 2","team 3","nrdb_id"]
    with open('OUTPUT/sync_bre.csv', newline='') as f:
        reader = csv.reader(f)
        for line in reader:
            if name.lower() in (line[0].lower(), line[1].lower(), line[2].lower()):
                try:
                    return int(line[6])
                except ValueError:
                    return None
    return None

def determine_teams(name: str) -> list:
    teams = None
    try:
        teams = determine_teams_from_bre(name)
    except:
        pass
    if teams:
        return teams
    return ['','','']

def determine_teams_from_bre(name: str) -> list:
    # expect csv to be in the format ["player name","player alias","player alias 2","testing team","team 2","team 3","nrdb_id"]
    with open('OUTPUT/sync_bre.csv', newline='') as f:
        reader = csv.reader(f)
        for line in reader:
            if name.lower() in (line[0].lower(), line[1].lower(), line[2].lower()):
                return [line[3],line[4],line[5]]
    return None

def determine_nrdb_name_from_csv(id: int) -> str:
    # expect csv to be in the format ["nrdb_name","nrdb_id"]
    with open('OUTPUT/nrdb_ids.csv', newline='') as f:
        reader = csv.reader(f)
        for line in reader:
            if int(line[1]) == int(id):
                return line[0]
    return None

def get_player_aliases(id: int) -> list:
    # expect csv to be in the format ["player name","player alias","player alias 2","testing team","team 2","team 3","nrdb_id"]
    with open('OUTPUT/sync_bre.csv', newline='') as f:
        reader = csv.reader(f)
        for line in reader:
            if id == line[6]:
                return [line[0],line[1],line[2]]
    return None

class TournamentPlayer:
    """
    A class representing a netrunner player at a tournament
    
    Attributes:
        name (str): the name under which the player registered for the tournament
        tournament_player_id (int): tournament id number of player
        nrdb_id (int): nrdb id number of player
        teams (list): a list of (3) teams that the player belongs to
        results (list): a 2d array of game results (the inner array is a dict)
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
    def __init__(self, tournament_player_id: int, name: str, corp_id: Identity, runner_id: Identity, swiss_rank: int, match_points: int, SoS: float, xSoS: float, side_balance: int = 0, cut_rank: int = ''):
        self.tournament_player_id = tournament_player_id
        self.name = name
        self.nrdb_id = determine_nrdb_id(self.name)
        self.teams = determine_teams(self.name)
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
        self.results = []

    def record_corp_result(self, game_data: dict):
        self.results.append(game_data)
        match game_data['result']:
            case 'corp':
                self.corp_wins += 1
            case 'runner':
                self.corp_losses += 1
            case 'draw':
                self.corp_draws += 1

    def record_runner_result(self, game_data: dict):
        self.results.append(game_data)
        match game_data['result']:
            case 'runner':
                self.runner_wins += 1
            case 'corp':
                self.runner_losses += 1
            case 'draw':
                self.runner_draws += 1

class Player:
    """
    A class representing a netrunner player (across multiple tournaments)
    
    Attributes:
        nrdb_id (int): nrdb id number of the player
        nrdb_name (str): the nrdb name of the player
        aliases (list): a list of (3) aliases by which the player is known        
        teams (list): a list of (3) teams to which the player belongs
        placements (dict): a 2d dictionary of tournament placements (keyed by tournament_id)
        results (dict): a 3d array of game results (the outer array is a dict keyed by tournament_id)
    """
    def __init__(self, nrdb_id: int, player_data: dict = None):
        self.nrdb_id = nrdb_id
        self.nrdb_name = determine_nrdb_name_from_csv(self.nrdb_id)
        self.aliases = get_player_aliases(self.nrdb_id)
        self.teams = determine_teams(self.nrdb_name)
        if player_data:
            self.placements = player_data.placements
            self.results = player_data.results
        else:
            self.placements = {}
            self.results = {}
        
    def add_tournament_results(self, tournament_id: str, t_player: TournamentPlayer, date: str = None, region: str = None, online: str = None, tournament_name: str = None, meta: str = None, force: bool = False):
        """ adds the results and final placement from a tournemnt to the player object """
        if not self.placements.get(tournament_id) or force:
            placement = {'meta': meta, 'date': date, 'region': region, 'online': online, 'tournament_name': tournament_name, 'cut_rank': t_player.cut_rank, 'swiss_rank': t_player.swiss_rank, 'corp_id': t_player.corp_id.name, 'runner_id': t_player.runner_id.name, 'corp_faction': t_player.corp_id.faction, 'runner_faction': t_player.runner_id.faction, 'corp_wins': t_player.corp_wins, 'corp_losses': t_player.corp_losses, 'corp_draws': t_player.corp_draws, 'runner_wins': t_player.runner_wins, 'runner_loses': t_player.runner_losses, 'runner_draws': t_player.runner_draws}
            self.placements[tournament_id] = placement

        if not self.results.get(tournament_id) or force:
            self.results[tournament_id] = t_player.results