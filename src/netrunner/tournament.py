import requests
from netrunner.identity import Identity

def get_json(url: str):
    json_url = url.strip() + '.json'
    resp = requests.get(url=json_url, params='')
    return resp.json()

def is_player_in_top_cut(eliminationPlayers: list, player_id: str) -> bool:
  for topcutplayer in eliminationPlayers:
      if player_id == topcutplayer['id']:
          return True
  return False

def find_player_in_top_cut(eliminationPlayers: list, player_id: str):
  return next(topcutplayer for topcutplayer in eliminationPlayers if topcutplayer['id'] == player_id)

class Tournament:
  def __init__(self, name: str, url: str, date: str = 'unknown', region: str = 'unknown', online: bool = False):
    self.name = name
    self.date = date
    self.region = region
    self.online = online
    self.json = get_json(url)

    self.standings = []
    for player in self.json['players']:
      standing = [] # this would probably be improved by being a dictionary tbh
      player_results = self.return_player_results(player['id'])
      runner_id = Identity(player['runnerIdentity'])
      corp_id = Identity(player['corpIdentity'])
      if is_player_in_top_cut(self.json['eliminationPlayers'], player['id']):
        top_cut_rank = find_player_in_top_cut(self.json['eliminationPlayers'], player['id']).get('rank')
      else:
        top_cut_rank = ''
      standing.extend([top_cut_rank, player['rank'], player['name'], corp_id.short_name, str(player_results['corp_wins']), str(player_results['corp_losses']), str(player_results['corp_draws']), runner_id.short_name, str(player_results['runner_wins']), str(player_results['runner_losses']), str(player_results['runner_draws']), player['matchPoints'], player['strengthOfSchedule'], player['extendedStrengthOfSchedule'], corp_id.name, corp_id.faction, runner_id.name, runner_id.faction])
      self.standings.append(standing)

  def return_player_results(self, player_id: str):
     pass

class AesopsTournament(Tournament):
   def return_player_results(self, player_id: str):
      player_results = { 'corp_wins': 0, 'corp_losses': 0, 'corp_draws': 0, 'runner_wins': 0, 'runner_losses': 0, 'runner_draws': 0 }
      for round in self.json['rounds']:
          for table in round:
              # did player play at this table?
              if player_id == table['corpPlayer']:
                  if 'eliminationGame' in table and table['eliminationGame']:
                      if player_id == table['winner_id']:
                          player_results['corp_wins'] += 1
                      else:
                          player_results['corp_losses'] += 1
                  else:
                      match table['corpScore']:
                          case "3":
                              player_results['corp_wins'] += 1
                          case "1":
                              player_results['corp_draws'] += 1
                          case "0":
                              player_results['corp_losses'] += 1
              elif player_id == table['runnerPlayer']:
                  if 'eliminationGame' in table and table['eliminationGame']:
                      if player_id == table['winner_id']:
                          player_results['runner_wins'] += 1
                      else:
                          player_results['runner_losses'] += 1
                  else:
                      match table['runnerScore']:
                          case "3":
                              player_results['runner_wins'] += 1
                          case "1":
                              player_results['runner_draws'] += 1
                          case "0":
                              player_results['runner_losses'] += 1
                          case _:
                              player_results['runner_draws'] += 1
      return player_results     
   
class CobraTournament(Tournament):
   def return_player_results(self, player_id: str):
      player_results = { 'corp_wins': 0, 'corp_losses': 0, 'corp_draws': 0, 'runner_wins': 0, 'runner_losses': 0, 'runner_draws': 0 }
      for round in self.json['rounds']:
          for table in round:
              # did player play at this table?
              if table['intentionalDraw'] or table['twoForOne']:
                  continue
              elif player_id == table['player1']['id']:
                  scores = table['player1']
              elif player_id == table['player2']['id']:
                  scores = table['player2']
              else:
                  continue
              # add cut result
              if table['eliminationGame']:
                  match scores['role']:
                      case 'corp':
                          if scores['winner']:
                              player_results['corp_wins'] += 1
                          else:
                              player_results['corp_losses'] += 1
                      case 'runner':
                          if scores['winner']:
                              player_results['runner_wins'] += 1
                          else:
                              player_results['runner_losses'] += 1
              # add swiss results
              else:
                  match scores['runnerScore']:
                      case 3:
                          player_results['runner_wins'] += 1
                      case 1:
                          player_results['runner_draws'] += 1
                      case 0:
                          player_results['runner_losses'] += 1
                  match scores['corpScore']:
                      case 3:
                          player_results['corp_wins'] += 1
                      case 1:
                          player_results['corp_draws'] += 1
                      case 0:
                          player_results['corp_losses'] += 1
      return player_results