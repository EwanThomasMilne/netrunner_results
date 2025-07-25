from netrunner.identity import Identity
from netrunner.player import TournamentPlayer
from abc import ABC, abstractmethod

def is_player_in_top_cut(eliminationPlayers: list, player_id: str) -> bool:
  for topcutplayer in eliminationPlayers:
      if player_id == topcutplayer['id']:
          return True
  return False

def find_player_in_top_cut(eliminationPlayers: list, player_id: str) -> dict:
    return next(topcutplayer for topcutplayer in eliminationPlayers if topcutplayer['id'] == player_id)

class Tournament(ABC):
    """
    A class representing a netrunner tournament

    Attributes:
        name (str): tournament name
        date (str): date of tournament
        location (str): tournament location
        region (str): tournament region
        json (dict): raw tournament data
        players (dict): a dictionary of Player objects,  keyed by each players tournament_player_id
        results (list): a 2d array of game results
        standings (list): a 2d array of player standings
        style (str): either DSS or SSS
        format (str): NSG netrunner format (defaults to standard)
        meta (str): Ban List Identifier
    """
    def __init__(self, json: dict, name: str = None, date: str = None, location: str = None, region: str = None, player_mappings: dict = {}, abr_id: int = None, style: str = None, format: str = 'standard', meta: str = None):
        self.name = name
        self.date = date
        self.location = location
        self.region = region
        self.abr_id = abr_id
        self.style = style
        self.format = format
        self.meta = meta
        self.json = json

        if self.date is None:
            self.date = self.json.get('date',None)
        if self.name is None:
            self.name = self.json.get('name',None)
        
        # build player objects
        self.players = {}
        for player in self.json['players']:
            corp_id = Identity(player['corpIdentity'])
            runner_id = Identity(player['runnerIdentity'])
            if is_player_in_top_cut(self.json['eliminationPlayers'], player['id']):
                top_cut_rank = find_player_in_top_cut(self.json['eliminationPlayers'], player['id']).get('rank')
            else:
                top_cut_rank = ''
            nrdb_id = player_mappings.get(player['name'],None)
            self.players[player['id']] = TournamentPlayer(tournament_player_id=player['id'], name=player['name'], corp_id=corp_id, runner_id=runner_id, swiss_rank=player['rank'], match_points=player['matchPoints'], SoS=player['strengthOfSchedule'], xSoS=player['extendedStrengthOfSchedule'], side_balance=player.get('sideBalance',0), cut_rank=top_cut_rank, nrdb_id=nrdb_id)

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
    
    @abstractmethod
    def process_swiss_table(self, round_num: int, table: dict):
        ...
    
    @abstractmethod
    def process_cut_table(self, round_num: int, table: dict):
        ...

    def determine_runner_and_corp_players(self, table: dict) -> tuple[str]:
        if table['player1']['role'] == 'runner':
            runner_player = self.players[table['player1']['id']]
            corp_player = self.players[table['player2']['id']]
        else:
            runner_player = self.players[table['player2']['id']]
            corp_player = self.players[table['player1']['id']]
        
        return runner_player, corp_player
        

class AesopsTournament(Tournament):
    def process_swiss_table(self, round_num: int, table: dict):
        phase = 'swiss'
        # if either player_id is null, assume this round was a Bye and do not record the results
        if table['player1']['id'] is None or table['player2']['id'] is None:
            return
        
        runner_player, corp_player = self.determine_runner_and_corp_players(table)
        result = 'unknown'
        corp_score = table['player1']['corpScore']
        runner_score = table['player1']['runnerScore']
        if corp_score == 1 or runner_score == 1:
            result = 'draw'
        elif corp_score == 3 or runner_score == 0:
            result = 'corp'
        else:
            result = 'runner'
        if table['intentionalDraw']:
            result = 'ID'
        
        game_data = { 'phase': phase, 'round': round_num, 'table': table['tableNumber'], 'corp_player': corp_player.name, 'corp_player_nrdb_id': corp_player.nrdb_id, 'corp_id': corp_player.corp_id.name, 'corp_faction':corp_player.corp_id.faction, 'result': result, 'runner_player': runner_player.name, 'runner_player_nrdb_id': runner_player.nrdb_id, 'runner_id': runner_player.runner_id.name, 'runner_faction': runner_player.runner_id.faction }
        self.results.append(game_data)
        runner_player.record_runner_result(game_data)
        corp_player.record_corp_result(game_data)

    def process_cut_table(self, round_num: int, table: dict):
        phase = 'cut'
        runner_player, corp_player = self.determine_runner_and_corp_players(table)
        result = 'unknown'
        corp_score = table['player1']['corpScore']
        runner_score = table['player1']['runnerScore']
        if corp_score == 0 or runner_score == 3:
            result = 'runner'
        else:
            result = 'corp'
        game_data = { 'phase': phase, 'round': round_num, 'table': table['tableNumber'], 'corp_player': corp_player.name, 'corp_player_nrdb_id': corp_player.nrdb_id, 'corp_id': corp_player.corp_id.name, 'corp_faction': corp_player.corp_id.faction, 'result': result, 'runner_player': runner_player.name, 'runner_player_nrdb_id': runner_player.nrdb_id, 'runner_id': runner_player.runner_id.name, 'runner_faction': runner_player.runner_id.faction }
        self.results.append(game_data)
        runner_player.record_runner_result(game_data)
        corp_player.record_corp_result(game_data)    
   
class CobraTournament(Tournament):
    def process_cut_table(self, round_num: int, table: dict):
        phase = 'cut'
        runner_player, corp_player = self.determine_runner_and_corp_players(table)
        result = 'unknown'

        if table['player1']['winner']:
            result = table['player1']['role']
        else:
            result = table['player2']['role']
        game_data = { 'phase': phase, 'round': round_num, 'table': table['table'], 'corp_player': corp_player.name, 'corp_player_nrdb_id': corp_player.nrdb_id, 'corp_id': corp_player.corp_id.name, 'corp_faction': corp_player.corp_id.faction, 'result': result, 'runner_player': runner_player.name, 'runner_player_nrdb_id': runner_player.nrdb_id, 'runner_id': runner_player.runner_id.name, 'runner_faction': runner_player.runner_id.faction }
        self.results.append(game_data)
        runner_player.record_runner_result(game_data)
        corp_player.record_corp_result(game_data)

class CobraDSSTournament(CobraTournament):
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
        if (table['player1']['runnerScore'] is None) or (table['player1']['runnerScore'] + table['player2']['corpScore'] == 0):
            result = 'unknown'
        if table['intentionalDraw']:
            result = 'ID'
        if table['twoForOne']:
            if table['player1']['combinedScore'] == 6:
                result = '2-for-1 (runner player)'
            elif table['player2']['combinedScore'] == 6:
                result = '2-for-1 (corp player)'
            else:
                print("unknown winner of 2-for-1 - Round: "+str(round_num)+", Table: "+str(table['table']))
                result = '2-for-1'
        game_data = { 'phase': phase, 'round': round_num, 'table': table['table'], 'corp_player': corp_player.name, 'corp_player_nrdb_id': corp_player.nrdb_id, 'corp_id': corp_player.corp_id.name, 'corp_faction': corp_player.corp_id.faction, 'result': result, 'runner_player': runner_player.name, 'runner_player_nrdb_id': runner_player.nrdb_id, 'runner_id': runner_player.runner_id.name, 'runner_faction': runner_player.runner_id.faction }
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
        if (table['player2']['runnerScore'] is None) or (table['player2']['runnerScore'] + table['player1']['corpScore'] == 0):
            result = 'unknown'
        if table['intentionalDraw']:
            result = 'ID'
        if table['twoForOne']:
            if table['player1']['combinedScore'] == 6:
                result = '2-for-1 (corp player)'
            elif table['player2']['combinedScore'] == 6:
                result = '2-for-1 (runner player)'
            else:
                print("unknown winner of 2-for-1 - Round: "+str(round_num)+", Table: "+str(table['table']))
                result = '2-for-1'
        game_data = { 'phase': phase, 'round': round_num, 'table': table['table'], 'corp_player': corp_player.name, 'corp_player_nrdb_id': corp_player.nrdb_id, 'corp_id': corp_player.corp_id.name, 'corp_faction': corp_player.corp_id.faction,'result': result, 'runner_player': runner_player.name, 'runner_player_nrdb_id': runner_player.nrdb_id, 'runner_id': runner_player.runner_id.name, 'runner_faction': runner_player.runner_id.faction }
        self.results.append(game_data)
        runner_player.record_runner_result(game_data)
        corp_player.record_corp_result(game_data)

class CobraSSSTournament(CobraTournament):
    def process_swiss_table(self, round_num: int, table: dict):
        phase = 'swiss'
        
        # if either player_id is null, assume this round was a Bye and do not record the results
        if table['player1']['id'] is None or table['player2']['id'] is None:
            return
        
        # figure out who is runner and who is corp
        if table['player1']['role'] == 'runner':
            runner = 'player1'
            runner_player = self.players[table['player1']['id']]
            corp_player = self.players[table['player2']['id']]
        else:
            runner = 'player2'
            runner_player = self.players[table['player2']['id']]
            corp_player = self.players[table['player1']['id']]

        # figure out the result
        result = 'unknown'
        match table[runner]['runnerScore']:
            case 3:
                result = 'runner'
            case 1:
                result = 'draw'
            case 0:
                result = 'corp'
        if table['intentionalDraw']:
            result = 'ID'

        # record the result
        game_data = { 'phase': phase, 'round': round_num, 'table': table['table'], 'corp_player': corp_player.name, 'corp_player_nrdb_id': corp_player.nrdb_id, 'corp_id': corp_player.corp_id.name, 'corp_faction': corp_player.corp_id.faction, 'result': result, 'runner_player': runner_player.name, 'runner_player_nrdb_id': runner_player.nrdb_id, 'runner_id': runner_player.runner_id.name, 'runner_faction': runner_player.runner_id.faction }
        self.results.append(game_data)
        runner_player.record_runner_result(game_data)
        corp_player.record_corp_result(game_data)

class ABRTournament(Tournament):
    def __init__(self, json: dict, name: str = None, date: str = None, region: str = None, location: str = None, player_mappings: dict = {}, abr_id: int = None, meta: str = None, style: str = None, format: str = 'standard'):
        self.name = name
        self.date = date
        self.region = region
        self.location = location
        self.abr_id = abr_id
        self.style = style
        self.format = format
        self.meta = meta
        self.json = json

        # build player objects
        self.players = {}
        for player in self.json:
            corp_id = Identity(player['corp_deck_identity_title'])
            runner_id = Identity(player['runner_deck_identity_title'])
            swiss_rank = player['rank_swiss']
            top_cut_rank = player['rank_top']
            player_name = player['user_import_name']
            nrdb_id = player_mappings.get(player['user_import_name'], player['user_id'])
            self.players[swiss_rank] = TournamentPlayer(tournament_player_id=swiss_rank, name=player_name, corp_id=corp_id, runner_id=runner_id, swiss_rank=swiss_rank, cut_rank=top_cut_rank, nrdb_id=nrdb_id, match_points=None, SoS=None, xSoS=None)

        # no tables to process
        self.results = []

        # build standings array
        self.standings = []
        for id, player in self.players.items():
            team1 = player.teams[0] if 0 < len(player.teams) else ''
            team2 = player.teams[1] if 1 < len(player.teams) else ''
            team3 = player.teams[2] if 2 < len(player.teams) else ''
            standing = [player.cut_rank, player.swiss_rank, player.name, team1, team2, team3, player.corp_id.short_name, str(player.corp_wins), str(player.corp_losses), str(player.corp_draws), player.runner_id.short_name, str(player.runner_wins), str(player.runner_losses), str(player.runner_draws), player.match_points, player.SoS, player.xSoS, player.corp_id.name, player.corp_id.faction, player.runner_id.name, player.runner_id.faction, player.nrdb_id]
            self.standings.append(standing)
