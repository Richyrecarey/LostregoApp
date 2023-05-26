
import pandas as pd
import streamlit as st
from utils import *
import numpy as np
import copy

@st.cache_data(ttl=15, show_spinner=False)
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
    # df = df.set_index("ID")
    # df = df.set_index("Hora")
    # df = df.set_index(["Hora", "Pista"], drop=False)
    # df.index.names = ['Hora', 'Pista']
    
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


def color_clasi(val):
    tamaño_grupo = len(val)
    # print(f"Dentro de color_clasi")
    # print(np.where(np.isin(val, [1,2]), "color: gold;", "color: silver;"))
    # Por ahora hardcodeado
    return np.where(np.isin(val, [1,2]), "color: gold;", "color: silver;")


def result_beautifier(result):
    aux = result.split("-")
    aux = [s.strip() for s in aux]
    return " - ".join(aux)

def obtener_grupo(horario, equipo):
    grupo = horario.loc[(horario["Equipo 1"] == equipo) | (horario["Equipo 2"] == equipo), "Grupo"].values[0]
    return int(grupo)

def obtener_competición(horario, equipo):
    competicion = horario.loc[(horario["Equipo 1"] == equipo) | (horario["Equipo 2"] == equipo), "Competición"].values[0]
    return competicion
    


def color(val, equipo_seleccionado):
    # print(f"Dentro de color con {equipo_seleccionado}")
    color = 'orange' if val==equipo_seleccionado else 'white'
    return f'color: {color}'

def formateo_columnas(cols):
    return ["background-color: dimgray; color:slategray"]*len(cols)


def get_group_classi(raw_data, team, competicion):
    # Esta esta mal
    # query = f'(`Equipo 1`=="{team}" | `Equipo 2`=="{team}") & Fase == "Grupos"'
    grupo_equipo = obtener_grupo(raw_data, team)
    query = f'(Grupo =={grupo_equipo}) & (Fase == "Grupos") & (Competición == "{competicion}")'
    print(query)
    aux = raw_data.query(query)
    print(aux)
    
    group_teams = pd.unique(aux[['Equipo 1', 'Equipo 2']].values.ravel('K')).tolist()
    # print(group_teams)
    
    default_dict = {
        "Equipo": "",
        "P. Ganados": 0,
        "P. Perdidos": 0,
        "Dif. Puntos": 0,
    }
    
    group_info = {}
    for team in group_teams:
        _temp = copy.deepcopy(default_dict)
        _temp["Equipo"] = team
        group_info[team] = _temp
    
    
    # Iteramos por el dataframe
    for index, row in aux.iterrows():
        # Quién ganó el partido?
        # print(row)
        # print(type(row["Resultado"]))
        if row["Resultado"] != "Pendiente":
            equipo_ganador = which_team_won(row["Resultado"])
            diferencia_puntos = int(row["Resultado"].split(" - ")[0]) - int(row["Resultado"].split(" - ")[1])
            # print(diferencia_puntos)
            
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
    print(group_info)
    ret = ret.sort_values(by = ["P. Ganados", "Dif. Puntos"], ascending=[False,False])
    ret = ret.reset_index(drop=True)
    ret.index += 1
    # ret.index = ret.index.astype("str") + "o"
    ret.index.name = 'Pos.'
    
    # .style.applymap(color, subset=['Equipo']).format({'Dif. Puntos':'{:+d}'})
    return ret

def format_group_classi(df, equipo):
    return df.style.apply_index(color_clasi).applymap(color, subset=['Equipo'], equipo_seleccionado = equipo).format({'Dif. Puntos':'{:+d}'})
    


def get_group_sum_up(group_classi_df, team):
    
    tamaño_grupo = group_classi_df.shape[0]
    
