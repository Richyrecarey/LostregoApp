
import pandas as pd
import streamlit as st
from utils import *
import numpy as np
import copy

@st.cache_data(ttl=15)
def load_data():
    csv_url = "https://docs.google.com/spreadsheets/d/1JOj1lYQkPVXzWKu0FqmVu6xj4SoZxKa7YqQ2YWO9fXE/export?format=csv&gid=0"
    df = pd.read_csv(csv_url)
    
    convert_dict = {
        'Grupo': 'Int64',
        'Pista': 'Int64'
    }
    
    df = df.astype(convert_dict, errors='raise')
    
    # print(df.dtypes)

    df = df.sort_values(by = ["Hora", "Pista"])
    df.reset_index()
    df.index += 1 

    # No se usa en principio
    df['IndexByField'] = df.sort_values(['Pista','Hora'], ascending=[True, True]).groupby(['Pista']).cumcount() + 1   
                
    df["ID"] = "P" + df["Pista"].astype(str) + "G" + df["Grupo"].astype(str) + "-" + df.index.astype(str)
    df = df.set_index("ID")
    
    df["Resultado"] = np.where(df["Resultado"].isnull(), "Pendiente", df["Resultado"])
    df["Resultado"] = df["Resultado"].transform(result_beautifier)
    # df["Equipo_Ganador"] = df["Resultado"].transform(which_team_won)
    
    
    return df


def which_team_won(result):
    _aux = result.split("-")
    if int(_aux[0].strip()) < int(_aux[1].strip()):
        return 2
    else:
        return 1



def bold(val):
    return "font-weight: bold"


def result_beautifier(result):
    aux = result.split("-")
    aux = [s.strip() for s in aux]
    return " - ".join(aux)



def get_group_classification(raw_data, team):
    query = f'(`Equipo 1`=="{team}" | `Equipo 2`=="{team}") & Fase == "Grupos"'
    aux = raw_data.query(query)
    # print(aux)
    
    team_group = aux["Grupo"].values[0]
    # print(team_group)
    
    group_teams = pd.unique(aux[['Equipo 1', 'Equipo 2']].values.ravel('K')).tolist()
    # print(group_teams)
    
    default_dict = {
        "Equipo": "",
        "P. Ganados": 0,
        "P. Perdidos": 0,
        "Dif. Puntos": 0,
    }
    
    group_info = {team: copy.deepcopy(default_dict) for team in group_teams}
    # print(group_info)
    # print(group_info.values())
    
    # Iteramos por el dataframe
    for index, row in aux.iterrows():
        # Quién ganó el partido?
        # print(row)
        # print(type(row["Resultado"]))
        if row["Resultado"] != "Pendiente":
            equipo_ganador = which_team_won(row["Resultado"])
            diferencia_puntos = int(row["Resultado"].split(" - ")[0]) - int(row["Resultado"].split(" - ")[1])
            print(diferencia_puntos)
            
            # Equipo 1
            group_info[row["Equipo 1"]]["Equipo"] = row["Equipo 1"]
            group_info[row["Equipo 1"]]["P. Ganados"] = group_info[row["Equipo 1"]]["P. Ganados"] + 1 if equipo_ganador == 1 else group_info[row["Equipo 1"]]["P. Ganados"]
            group_info[row["Equipo 1"]]["P. Perdidos"] = group_info[row["Equipo 1"]]["P. Perdidos"] + 1 if equipo_ganador == 2 else group_info[row["Equipo 1"]]["P. Perdidos"]
            group_info[row["Equipo 1"]]["Dif. Puntos"] = group_info[row["Equipo 1"]]["Dif. Puntos"] + diferencia_puntos
            
            # Equipo 2
            group_info[row["Equipo 2"]]["Equipo"] = row["Equipo 2"]
            group_info[row["Equipo 2"]]["P. Ganados"] = group_info[row["Equipo 2"]]["P. Ganados"] + 1 if equipo_ganador == 2 else group_info[row["Equipo 2"]]["P. Ganados"]
            group_info[row["Equipo 2"]]["P. Perdidos"] = group_info[row["Equipo 2"]]["P. Perdidos"] + 1 if equipo_ganador == 1 else group_info[row["Equipo 2"]]["P. Perdidos"]
            group_info[row["Equipo 2"]]["Dif. Puntos"] = 0
            group_info[row["Equipo 2"]]["Dif. Puntos"] = group_info[row["Equipo 2"]]["Dif. Puntos"] - diferencia_puntos

            
        
        
    # print(group_info.values())
    ret = pd.DataFrame.from_dict(group_info.values())
    ret = ret.sort_values(by = ["P. Ganados", "Dif. Puntos"], ascending=[False,False])
    ret = ret.reset_index(drop=True)
    ret.index += 1
    return ret
