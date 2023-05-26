
import pandas as pd
import streamlit as st
from utils import *
import copy

def color(val):
    color = 'orange' if val==equipo else 'white'
    return f'color: {color}'

"""


# :zap: II Torneo Lóstrego :zap:
En esta app (v.1.0.1) podrás consultar los horarios y resultados del torneo en tiempo real.

Si te gusta el evento, no olvides seguirnos en [Instagram](https://www.instagram.com/lostregoclubdevolei/), y escribirnos una reseña en [Google](https://g.page/r/Cc8en1zkeIWgEB0/review)! :wink: 

---
"""

cols_to_show = ["Hora", "Pista", "Grupo", "Equipo 1", "Equipo 2", "Resultado", "Árbitro"]
cols_to_show_1 = ["Hora", "Pista", "Equipo 1", "Equipo 2", "Resultado", "Árbitro"]
cols_to_show_total = ["Competición", "Hora", "Pista", "Fase", "Grupo", "Equipo 1", "Equipo 2", "Resultado", "Árbitro"]
cols_to_show_total2 = ["Competición", "Hora", "Pista", "Grupo", "Equipo 1", "Equipo 2", "Resultado", "Árbitro"]



df_horario = load_data()
# print(df_horario)

equipos = pd.unique(df_horario[['Equipo 1', 'Equipo 2']].dropna().values.ravel('K')).tolist()
equipos.sort()
equipos.insert(0, "Todos los equipos")
equipos.insert(0, "")

pistas = df_horario.Pista.dropna().unique().tolist()
pistas.insert(0, "Todas las pistas")

# grupos = df_horario.Grupo.dropna().unique().tolist()
# grupos.insert(0, "Todos los grupos")

competiciones = df_horario.Competición.dropna().unique().tolist()
competiciones.insert(0, "Todas las competiciones")


competicion = st.selectbox('Competición', competiciones, key = "competicion")
# No lo filtramos para que aparezcan también los partidos en los que arbitra un equipo
# df_horario = df_horario[(df_horario["Competición"] == competicion)]
    
     
# equipos = pd.unique(df_horario[['Equipo 1', 'Equipo 2']].values.ravel('K')).tolist()   
# equipos.insert(0, "Todos los equipos")
equipo = st.selectbox('Buscar tu equipo, o selecciona "Todos los equipos" para ver el horario completo', equipos)

if (equipo == "Todos los equipos") & (competicion != "Todas las competiciones"):
    df_horario = df_horario[(df_horario["Competición"] == competicion)]

st.markdown("---")

if (equipo == equipos[0]):
    pass

elif equipo == equipos[1]:
    # Si elegimos todo, mostramos todo!
    
    # Primero mostramos los partidos de grupos:
    st.write(f'Horario de grupos:')
    # TODO: Hay que añadir quién gana cada partido, poniéndolo por ejemplo en negrita
    # TODO: Añadir aquí si el partido está pendiente, en juego,etc... haciendo uso de una nueva columnade RESULTADO quizás
    st.dataframe(df_horario[cols_to_show_total2].set_index("Hora").sort_index())
    
    
    
else:
    # print("obteniendo grupo...")
    grupo = obtener_grupo(df_horario, equipo)
    # Competición del equipo seleccionado
    
    competicion_equipo = obtener_competición(df_horario, equipo)
    # Si se ha seleccionado algún equipo, filtramos
    # 1. Nos quedamos solo con los partidos que juega ese equipo
    df_horario_grupos_equipo = df_horario[(df_horario["Fase"] == "Grupos")]
    df_horario_grupos_equipo = df_horario_grupos_equipo[(df_horario_grupos_equipo["Equipo 1"] == equipo) | (df_horario_grupos_equipo["Equipo 2"] == equipo) | (df_horario_grupos_equipo["Árbitro"] == equipo)]
    

    st.write(f'Horario de grupos para :orange[{equipo}] (Grupo {grupo} - {competicion_equipo})')
    p_arbitrar_grp = df_horario_grupos_equipo[(df_horario_grupos_equipo["Árbitro"] == equipo)].shape[0]
    
    if p_arbitrar_grp > 0:
        st.caption(f':warning: Incluye :orange[{p_arbitrar_grp}] partido{"s" if p_arbitrar_grp > 1 else ""} de grupos a arbitrar')
    else:
        st.caption(f':ballot_box_with_check: No tenéis que arbitrar ningún partido de grupos')
    

    # st.caption(f'Horario para :orange[{equipo}] en el grupo N (incluye partidos a arbitrar):')
    st.dataframe(df_horario_grupos_equipo[cols_to_show_1].set_index("Hora").style.applymap(color, subset=['Equipo 1', 'Equipo 2', 'Árbitro']).applymap(bold, subset=['Equipo 1', 'Equipo 2']))
    
    
    # CLASIFICACION GRUPOS
    df_horario_grupo_equipo = df_horario[(df_horario["Fase"] == "Grupos") | (df_horario["Grupo"] == grupo) | (df_horario["Competición"] == competicion_equipo)]
    
    st.write(f'Clasificación Grupo {grupo} - {competicion_equipo}')
    st.dataframe(format_group_classi(get_group_classi(df_horario_grupo_equipo, equipo, competicion_equipo), equipo))
    st.caption("Pasarán a categoría oro los 2 primeros, y a plata los 2 últimos.")
    
    # Eliminatorias

    st.markdown(f'Partidos de eliminatorias para :orange[{equipo}]')
    

    # Horario clasificaciones
    df_horario_elim = df_horario[(df_horario["Fase"] != "Grupos")]
    df_horario_elim = df_horario_elim[(df_horario_elim["Equipo 1"] == equipo) | (df_horario_elim["Equipo 2"] == equipo) | (df_horario_elim["Árbitro"] == equipo)].set_index("Hora")
    
    # TODO: Hay que buscar la categoría del equipo
    
    if df_horario_elim.empty:
        st.info(f"""Los partidos de eliminatoria aún no están disponibles para :orange[{equipo}].""", icon="ℹ️")
    else:
        # cols_to_show2 = ["Hora", "Pista", "Fase","Equipo 1", "Equipo 2", "Resultado", "Árbitro"]
        cols_to_show2 = ["Fase","Pista","Equipo 1", "Equipo 2", "Resultado", "Árbitro"]
        st.dataframe(df_horario_elim[cols_to_show2].style.applymap(color, subset=['Equipo 1', 'Equipo 2']).applymap(bold, subset=['Equipo 1', 'Equipo 2']))
        
        p_arbitrar_elim = df_horario_elim[(df_horario_elim["Árbitro"] == equipo)].shape[0]
    
        if p_arbitrar_elim > 0:
            st.caption(f':warning: Incluye :orange[{p_arbitrar_elim}] partido{"s" if p_arbitrar_elim > 1 else ""} de eliminatorias a arbitrar')
        else:
            st.caption(f'No tenéis que arbitrar ningún partido de eliminatorias')


    
    
    

