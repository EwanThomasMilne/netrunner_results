class Players:

    def __init__(self, player_dict) -> None:
        self.player_dict = player_dict
        
    # takes a player's cobra id and a side and returns their id for that side
    def get_identity(self, player_id: int, role: str) -> str:
        for player in self.player_dict:
            if player['id'] == player_id:
                return player[role+'Identity']


class Identities:
    
    def __init__(self) -> None:
            
        self.identities = {}
        
    #TODO: move the for loop into the results class somehow
    def generate_rows(self):
        for identity, values in self.identities.items():
            yield [identity, values["wins"], values["draws"], values["loses"]] 
            
    def add_result(self, identity: str, result: str):
        
        if identity not in self.identities:
            self.identities.update({identity: {'wins': 0, 'draws': 0, 'loses': 0}})
            
        self.identities[identity][result] += 1


class Results:
    
    def __init__(self) -> None:
        self.identities = Identities()
        
    def generate_report(self):
        
        result = [['id','wins','draws','loses']]
        for row in self.identities.generate_rows():
            result.append(row)
            
        return result