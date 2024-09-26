import json
from netrunner.identity import Identity

def get_player_details_by_id(nrdb_id: int) -> dict:
    with open('players.json') as f:
        players = json.load(f)
    return players[str(nrdb_id)]

def get_player_details_by_name(name: str) -> dict:
    with open('players.json') as f:
        players = json.load(f)
    for id,player in players.items():
        if name.strip().lower() == player.get('nrdb_name','').lower():
            player['nrdb_id'] = int(id)
            return player
        for alias in player.get('aliases',[]):
            if name.strip().lower() == alias.lower():
                player['nrdb_id'] = int(id)
                return player
    #print("could not find "+name+" in players.json")
    return {}

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
    def __init__(self, tournament_player_id: int, name: str, corp_id: Identity, runner_id: Identity, swiss_rank: int, match_points: int, SoS: float, xSoS: float, side_balance: int = 0, cut_rank: int = '', nrdb_id: int = None):
        self.tournament_player_id = tournament_player_id
        self.name = name
        if nrdb_id:
            self.nrdb_id = int(nrdb_id)
            player_details = get_player_details_by_id(self.nrdb_id)
        else:
            player_details = get_player_details_by_name(self.name)
            self.nrdb_id = player_details.get('nrdb_id',None)
        self.teams = player_details.get('teams',[])
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
    Parameters:
        nrdb_id (int): nrdb id number of the player
    
    Attributes:
        nrdb_id (int): nrdb id number of the player
        nrdb_name (str): the nrdb name of the player
        aliases (list): a list of (3) aliases by which the player is known        
        teams (list): a list of (3) teams to which the player belongs
        tournaments (dict): a dictionary of tournament attendance (keyed by tournament_id)
            games (list): an array of game results from the tournament
    """
    def __init__(self, nrdb_id: int, player_data: dict = None):
        self.nrdb_id = nrdb_id
        player_details = get_player_details_by_id(self.nrdb_id)
        self.nrdb_name = player_details.get('nrdb_name',None)
        self.aliases = player_details.get('aliases',None)
        self.teams = player_details.get('teams',None)
        if player_data:
            self.tournaments = player_data.tournaments
        else:
            self.tournaments = {}
        
    def add_tournament_results(self, tournament_id: str, t_player: TournamentPlayer, date: str = None, region: str = None, online: str = None, tournament_name: str = None, tournament_url: str = None, tournament_level: str = None, meta: str = None, size: int = None, abr_id: str = None, force: bool = False):
        """ adds the results and final placement from a tournemnt to the player object """
        if not self.tournaments.get(tournament_id) or force:
            placement = {'meta': meta, 'date': date, 'region': region, 'online': online, 'tournament_name': tournament_name, 'tournament_url': tournament_url, 'tournament_size': size, 'tournament_level': tournament_level, 'abr_id': abr_id, 'cut_rank': t_player.cut_rank, 'swiss_rank': t_player.swiss_rank, 'corp_id': t_player.corp_id.name, 'runner_id': t_player.runner_id.name, 'corp_faction': t_player.corp_id.faction, 'runner_faction': t_player.runner_id.faction, 'corp_wins': t_player.corp_wins, 'corp_losses': t_player.corp_losses, 'corp_draws': t_player.corp_draws, 'runner_wins': t_player.runner_wins, 'runner_loses': t_player.runner_losses, 'runner_draws': t_player.runner_draws}
            self.tournaments[tournament_id] = placement
            self.tournaments[tournament_id]['games'] = t_player.results