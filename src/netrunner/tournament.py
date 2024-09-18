from netrunner.identity import Identity
from netrunner.player import TournamentPlayer

def is_player_in_top_cut(eliminationPlayers: list, player_id: str) -> bool:
  for topcutplayer in eliminationPlayers:
      if player_id == topcutplayer['id']:
          return True
  return False

def find_player_in_top_cut(eliminationPlayers: list, player_id: str) -> dict:
    return next(topcutplayer for topcutplayer in eliminationPlayers if topcutplayer['id'] == player_id)

class Tournament:
    """
    A class representing a netrunner tournament

    Attributes:
        name (str): tournament name
        date (str): date of tournament
        region (str): tournament region
        online (bool): netspace or meatspace
        json (dict): raw tournament data
        players (dict): a dictionary of Player objects,  keyed by each players tournament_player_id
        results (list): a 2d array of game results
        standings (list): a 2d array of player standings
    """
    def __init__(self, json: dict, name: str = None, date: str = None, region: str = None, online: bool = False):
        self.name = name
        self.date = date
        self.region = region
        self.online = online
        self.json = json

        if self.date is None:
            self.date = self.json['date']
        if self.name is None:
            self.name = self.json['name']
        
        # build player objects
        self.players = {}
        for player in self.json['players']:
            corp_id = Identity(player['corpIdentity'])
            runner_id = Identity(player['runnerIdentity'])
            if is_player_in_top_cut(self.json['eliminationPlayers'], player['id']):
                top_cut_rank = find_player_in_top_cut(self.json['eliminationPlayers'], player['id']).get('rank')
            else:
                top_cut_rank = ''
            self.players[player['id']] = TournamentPlayer(tournament_player_id = player['id'], name = player['name'], corp_id = corp_id, runner_id = runner_id, swiss_rank = player['rank'], match_points = player['matchPoints'], SoS = player['strengthOfSchedule'], xSoS = player['extendedStrengthOfSchedule'], side_balance = player.get('sideBalance',0), cut_rank = top_cut_rank)

        # process tables
        self.results = []
        round_num = 1
        for round in self.json['rounds']:
            for table in round:
                if table.get('eliminationGame',False):
                    self.process_cut_table(round_num, table)
                else:
                    self.process_swiss_table(round_num, table)
            round_num += 1

        # build standings array
        self.standings = []
        for id, player in self.players.items():
            team1 = player.teams[0] if 0 < len(player.teams) else ''
            team2 = player.teams[1] if 1 < len(player.teams) else ''
            team3 = player.teams[2] if 2 < len(player.teams) else ''
            standing = [player.cut_rank, player.swiss_rank, player.name, team1, team2, team3, player.corp_id.short_name, str(player.corp_wins), str(player.corp_losses), str(player.corp_draws), player.runner_id.short_name, str(player.runner_wins), str(player.runner_losses), str(player.runner_draws), player.match_points, player.SoS, player.xSoS, player.corp_id.name, player.corp_id.faction, player.runner_id.name, player.runner_id.faction, player.nrdb_id]
            self.standings.append(standing)

    def process_swiss_table(self, table: dict):
        # dummy method for inheritance
        pass
    def process_cut_table(self, table: dict):
        # dummy method for inheritance
        pass

class AesopsTournament(Tournament):
    def process_swiss_table(self, round_num: int, table: dict):
        phase = 'swiss'
        # if either player_id is '(BYE)', assume this round was a Bye and do not record the results
        if table['runnerPlayer'] == '(BYE)' or table['corpPlayer'] == '(BYE)':
            return

        runner_player = self.players[table['runnerPlayer']]
        corp_player = self.players[table['corpPlayer']]
        result = 'unknown'
        match table['runnerScore']:
            case '3':
                result = 'runner'
            case '1':
                result = 'draw'
            case '0':
                result = 'corp'
        game_data = { 'phase': phase, 'round': round_num, 'table': table['tableNumber'], 'corp_player': corp_player.name, 'corp_player_nrdb_id': corp_player.nrdb_id, 'corp_id': corp_player.corp_id.name, 'result': result, 'runner_player': runner_player.name, 'runner_player_nrdb_id': runner_player.nrdb_id, 'runner_id': runner_player.runner_id.name }
        self.results.append(game_data)
        runner_player.record_runner_result(game_data)
        corp_player.record_corp_result(game_data)

    def process_cut_table(self, round_num: int, table: dict):
        phase = 'cut'
        runner_player = self.players[table['runnerPlayer']]
        corp_player = self.players[table['corpPlayer']]
        result = 'unknown'
        if table['winner_id'] == table['runnerPlayer']:
            result = 'runner'
        else:
            result = 'corp'
        game_data = { 'phase': phase, 'round': round_num, 'table': table['tableNumber'], 'corp_player': corp_player.name, 'corp_player_nrdb_id': corp_player.nrdb_id, 'corp_id': corp_player.corp_id.name, 'result': result, 'runner_player': runner_player.name, 'runner_player_nrdb_id': runner_player.nrdb_id, 'runner_id': runner_player.runner_id.name }
        self.results.append(game_data)
        runner_player.record_runner_result(game_data)
        corp_player.record_corp_result(game_data)    
   
class CobraTournament(Tournament):
    def process_swiss_table(self, round_num: int, table: dict):
        phase = 'swiss'

        # if either player_id is null, assume this round was a Bye and do not record the results
        if table['player1']['id'] is None or table['player2']['id'] is None:
            return

        # Game 1 of DSS - player1 plays runner
        runner_player = self.players[table['player1']['id']]
        corp_player = self.players[table['player2']['id']]
        result = 'unknown'
        match table['player1']['runnerScore']: 
            case 3:
                result = 'runner'
            case 1:
                result = 'draw'
            case 0:
                result = 'corp'
        if table['player1']['runnerScore'] + table['player2']['corpScore'] == 0:
            result = 'unknown'
        if table['intentionalDraw']:
            result = 'ID'
        if table['twoForOne']:
            result = '2-for-1'
        game_data = { 'phase': phase, 'round': round_num, 'table': table['table'], 'corp_player': corp_player.name, 'corp_player_nrdb_id': corp_player.nrdb_id, 'corp_id': corp_player.corp_id.name, 'result': result, 'runner_player': runner_player.name, 'runner_player_nrdb_id': runner_player.nrdb_id, 'runner_id': runner_player.runner_id.name }
        self.results.append(game_data)
        runner_player.record_runner_result(game_data)
        corp_player.record_corp_result(game_data)
        
        # Game 2 of DSS - player1 plays corp
        runner_player = self.players[table['player2']['id']]
        corp_player = self.players[table['player1']['id']]
        result = 'unknown'
        match table['player1']['corpScore']: 
            case 3:
                result = 'corp'
            case 1:
                result = 'draw'
            case 0:
                result = 'runner'
        if table['player2']['runnerScore'] + table['player1']['corpScore'] == 0:
            result = 'unknown'
        if table['intentionalDraw']:
            result = 'ID'
        if table['twoForOne']:
            result = '2-for-1'
        game_data = { 'phase': phase, 'round': round_num, 'table': table['table'], 'corp_player': corp_player.name, 'corp_player_nrdb_id': corp_player.nrdb_id, 'corp_id': corp_player.corp_id.name, 'result': result, 'runner_player': runner_player.name, 'runner_player_nrdb_id': runner_player.nrdb_id, 'runner_id': runner_player.runner_id.name }
        self.results.append(game_data)
        runner_player.record_runner_result(game_data)
        corp_player.record_corp_result(game_data)

    def process_cut_table(self, round_num: int, table: dict):
        phase = 'cut'
        if table['player1']['role'] == 'runner':
            runner_player = self.players[table['player1']['id']]
            corp_player = self.players[table['player2']['id']]
        else:
            runner_player = self.players[table['player2']['id']]
            corp_player = self.players[table['player1']['id']]
        result = 'unknown'
        if table['player1']['winner']:
            result = table['player1']['role']
        else:
            result = table['player2']['role']
        game_data = { 'phase': phase, 'round': round_num, 'table': table['table'], 'corp_player': corp_player.name, 'corp_player_nrdb_id': corp_player.nrdb_id, 'corp_id': corp_player.corp_id.name, 'result': result, 'runner_player': runner_player.name, 'runner_player_nrdb_id': runner_player.nrdb_id, 'runner_id': runner_player.runner_id.name }
        self.results.append(game_data)
        runner_player.record_runner_result(game_data)
        corp_player.record_corp_result(game_data)
