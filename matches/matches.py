class PlayersWrapper:
    #provides methods for searching the players dictionary

    def __init__(self, player_dict) -> None:
        self.player_dict = player_dict
        
    # takes an identity name and standardises it (if necessary)
    def standardise_identity(self, identity: str) -> str:
        match identity:
            case 'Rielle "Kit" Peddler: Transhuman':
                identity = 'Rielle “Kit” Peddler: Transhuman'
            case 'Esa Afontov: Eco-Insurrectionist':
                identity = 'Esâ Afontov: Eco-Insurrectionist'
            case 'Tao Salonga: Telepresence Magician':
                identity = 'Tāo Salonga: Telepresence Magician'
            case 'Ayla "Bios" Rahim: Simulant Specialist':
                identity ='Ayla “Bios” Rahim: Simulant Specialist'
            case 'Sebastiao Souza Pessoa: Activist Organizer':
                identity = 'Sebastião Souza Pessoa: Activist Organizer'
            case 'Ken "Express" Tenma: Disappeared Clone':
                identity = 'Ken “Express” Tenma: Disappeared Clone'
            case 'Rene "Loup" Arcemont: Party Animal':
                identity = 'René “Loup” Arcemont: Party Animal'
        return identity

    # takes a player's cobra id and a side and returns their id for that side
    def get_identity(self, player_id: int, role: str) -> str:
        for player in self.player_dict:
            if player['id'] == player_id:
                return self.standardise_identity(player[role+'Identity'])

    # takes a player's cobra id and returns their name
    def get_name(self, player_id: int) -> str:
        for player in self.player_dict:
            if player['id'] == player_id:
                return player['name']


class TablesResultsByIdentity:
    #takes in tournament data and sorts it by identity rather than round
    
    def __init__(self) -> None:
        self.games = []
        
    def add_results_object(self, dateOfTournament, tournamentName, results_object):
        # takes another ResultsByIdentityObject (tournament?) and adds those results to this object
        for result in results_object.games:
            result['date'] = dateOfTournament
            result['tournamentName'] = tournamentName
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
        report = [[ 'date', 'tournament', 'phase', 'round', 'table', 'corp_player', 'corp_id', 'result', 'runner_player', 'runner_id' ]]
        
        for game in self.games:
            report.append([game['date'], game['tournamentName'], game['phase'], game['round'], game['table'], game['corp_player'], game['corp_id'], game['winner'], game['runner_player'], game['runner_id']])
        
        return report
