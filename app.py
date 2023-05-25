
import pandas as pd
import streamlit as st
from utils import *
import copy



def color(val):
    color = 'orange' if val==equipo else 'white'
    return f'color: {color}'

"""


# :zap: II Torneo Lóstrego :zap:
En esta app podrás encontrar todos los horarios y resultados en tiempo real de la competición.

Para cualquier duda, pásate por la carpa.

---
"""

cols_to_show = ["Hora", "Pista", "Grupo", "Equipo 1", "Equipo 2", "Resultado", "Árbitro"]



df_horario = load_data()


equipos = pd.unique(df_horario[['Equipo 1', 'Equipo 2']].values.ravel('K')).tolist()
equipos.insert(0, "Todos los equipos")
equipos.insert(0, "")

pistas = df_horario.Pista.dropna().unique().tolist()
pistas.insert(0, "Todas las pistas")

grupos = df_horario.Grupo.dropna().unique().tolist()
grupos.insert(0, "Todos los grupos")

competiciones = df_horario.Competición.dropna().unique().tolist()
# competicion.insert(0, "Todas las categorías")


competicion = st.selectbox('Competición', competiciones, key = "competicion")
# df_horario = df_horario[(df_horario["Competición"] == competicion)]
     
# equipos = pd.unique(df_horario[['Equipo 1', 'Equipo 2']].values.ravel('K')).tolist()   
# equipos.insert(0, "Todos los equipos")
equipo = st.selectbox('Buscar tu equipo, o selecciona "Todos" para ver todo el calendario', equipos)

st.markdown("---")

if (equipo == equipos[0]):
    pass

elif equipo == equipos[1]:
    # Si elegimos todo, mostramos todo!
    st.dataframe(df_horario[cols_to_show].style.applymap(color, subset=['Equipo 1', 'Equipo 2']).applymap(bold, subset=['Equipo 1', 'Equipo 2']))

else:
    # Si se ha seleccionado algún equipo, filtramos
    # 1. Nos quedamos solo con los partidos que juega ese equipo
    df_horario_grupos = df_horario[(df_horario["Fase"] == "Grupos")]
    df_horario_grupos = df_horario_grupos[(df_horario_grupos["Equipo 1"] == equipo) | (df_horario_grupos["Equipo 2"] == equipo) | (df_horario_grupos["Árbitro"] == equipo)]
    

    
    st.caption(f'Horario para :orange[{equipo}] en el grupo N (incluye partidos a arbitrar):')
    st.dataframe(df_horario_grupos[cols_to_show].style.applymap(color, subset=['Equipo 1', 'Equipo 2', 'Árbitro']).applymap(bold, subset=['Equipo 1', 'Equipo 2']))
    
    st.caption(f'Clasificación Grupo N - Pasarán a categoría oro los N primeros, y a plata los demás.')
    st.dataframe(get_group_classification(df_horario_grupos, equipo).style.applymap(color, subset=['Equipo']))

    st.caption(f'Partidos de eliminatorias para :orange[{equipo}] (incluye partidos a arbitrar):')
    st.markdown(f':dimgray[Partidos de eliminatorias para :orange[{equipo}] (incluye partidos a arbitrar)]')
    st.markdown(f"""<span style='color:grey'>Partidos de eliminatorias para  (incluye partidos a arbitrar)</span>""", unsafe_allow_html=True)
    
    df_horario_grupos = df_horario_grupos[(df_horario_grupos["Fase"] != "Grupos")]
    df_horario_grupos = df_horario_grupos[(df_horario_grupos["Equipo 1"] == equipo) | (df_horario_grupos["Equipo 2"] == equipo) | (df_horario_grupos["Árbitro"] == equipo)]
    
    # Horario clasificaciones
    df_horario_elim = df_horario[(df_horario["Fase"] != "Grupos")]
    df_horario_elim = df_horario_elim[(df_horario_elim["Equipo 1"] == equipo) | (df_horario_elim["Equipo 2"] == equipo) | (df_horario_elim["Árbitro"] == equipo)]
    
    if df_horario_elim.empty:
        st.info(f'Aún no están disponibles los partidos de clasificatoria para :orange[{equipo}]', icon="ℹ️")
    else:
        cols_to_show2 = ["Hora", "Pista", "Fase","Equipo 1", "Equipo 2", "Resultado", "Árbitro"]
        st.dataframe(df_horario_elim[cols_to_show2].style.applymap(color, subset=['Equipo 1', 'Equipo 2']).applymap(bold, subset=['Equipo 1', 'Equipo 2']))


    
    
    

