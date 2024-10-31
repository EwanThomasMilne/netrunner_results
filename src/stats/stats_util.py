import pandas as pd
import glob
from enum import Enum

class Meta(Enum):
    A = '20.06'
    B = '20.09'
    C = '21.04'
    D = '21.05'
    E = '21.06'
    F = '21.1'
    G = '22.08'
    H = '22.09'
    I = '23.03'
    J = '23.08'
    K = '23.09'
    L = '24.03'
    M = '24.05'
    N = '24.09'

def load_tornament_data(file_directory: str = "OUTPUT/results/") -> pd.DataFrame:
    tournament_data = pd.DataFrame()
    for file_name in glob.glob(file_directory+'*.csv'):
        x = pd.read_csv(file_name, low_memory=False)
        tournament_data = pd.concat([tournament_data, x],axis=0)

    tournament_data["runner_win"] = tournament_data.apply(lambda x: 1 if 'runner' in x['result'] else 0, axis=1)
    tournament_data["corp_win"] = tournament_data.apply(lambda x: 1 if 'corp' in  x['result'] else 0, axis=1)
    tournament_data["meta"] = tournament_data["meta"].astype(str)
    return tournament_data


def faction_winrates(tournament_data: pd.DataFrame):
    group = tournament_data.groupby(["runner_faction", "corp_faction"]).sum()
    group = group[["runner_win", "corp_win"]]
    return group
