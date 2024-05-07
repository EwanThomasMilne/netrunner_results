class PlayersWrapper:
    #provides methods for searching the players dictionary

    def __init__(self, player_dict) -> None:
        self.player_dict = player_dict
        
    # takes a player's cobra id and a side and returns their id for that side
    def get_identity(self, player_id: int, role: str) -> str:
        for player in self.player_dict:
            if player['id'] == player_id:
                return player[role+'Identity']


class ResultsByIdentityObject:
    #takes in tournament data and sorts it by identity rather than round
    
    def __init__(self) -> None:
        self.identities_dict = {}
        
    def add_new_identity(self, identity):
        self.identities_dict.update({identity: {'wins': 0, 'draws': 0, 'loses': 0}})
        
    def add_result(self, identity: str, result: str):
        # takes the name of a single id and adds a record of a single game result
        if identity not in self.identities_dict:
            self.add_new_identity(identity)
            
        self.identities_dict[identity][result] += 1
        
    def add_results_object(self, resultByIdentity):
        # takes another ResultsByIdentityObject and adds those results to this object
        for identity, winsdrawsloses in resultByIdentity.identities_dict.items():
            if identity not in self.identities_dict:
                self.add_new_identity(identity)
                
            self.identities_dict[identity]['wins'] += winsdrawsloses['wins']
            self.identities_dict[identity]['draws'] += winsdrawsloses['draws']
            self.identities_dict[identity]['loses'] += winsdrawsloses['loses']
        
    def add_tournament_data(self, rounds, players):
        # takes a dictionary of data about mutliple rounds in a tournament and adds it to the identities_dict
        for round in rounds:
            self.add_round_data(round, players)
    
    def add_round_data(self, round, players):
        # takes a dictionary of data about a round and adds it to the identities_dict
        for table in round:
            self.add_table_data(table, players)
    
    def add_table_data(self, table, players):
        # takes a dictionary of data about a cut match and adds it to the identities_dict
        pass #TODO: read about how to actually do a base class in python
    
    def add_swiss_table_data(self, table, players):
        # takes a dictionary of data about swiss a match and adds it to the identities_dict
        pass #TODO: read about how to actually do a base class in python
        
    def add_cut_table_data(self, table, players):
        # takes a dictionary of data about a match and adds it to the identities_dict
        pass #TODO: read about how to actually do a base class in python
    
    def generate_report(self):
        # generates a flat view of the results suitable for printing or outputting
        result = [['id','wins','draws','loses', 'winrate']]
        
        for identity, values in self.identities_dict.items():
            winrate = values["wins"] / (values["wins"] + values["draws"] + values["loses"])
            result.append([identity, values["wins"], values["draws"], values["loses"], round(winrate, 2)])
        
        return result
