import streamlit as st
import pandas as pd
import os
from pulp import LpMaximize, LpProblem, LpVariable, lpSum

# Fonction pour charger toutes les startlists
def load_startlists(directory):
    startlists = {}
    for file in os.listdir(directory):
        if file.endswith(".pkl"):
            course_name = os.path.splitext(file)[0]  # Nom de la course (sans extension)
            startlists[course_name] = pd.read_pickle(os.path.join(directory, file))
    return startlists

# Charger les données
startlist_dir = "./Race/"
startlists = load_startlists(startlist_dir)

# Sélectionner une course
st.title("Cycling Fantasy : prognostic optimization")
selected_course = st.selectbox("Select a race :", list(startlists.keys()))

# Afficher la startlist de la course sélectionnée
startlist = startlists[selected_course]
st.write(f"Startlist for {selected_course} :")
st.dataframe(startlist)

# Gestion des sélections
st.write("**Make your pronostic for the top20 :**")
selected_riders = []
for i in range(1, 21):
    available_riders = startlist[~startlist["Rider"].isin(selected_riders)]["Rider"]
    rider = st.selectbox(f"Position {i} :", available_riders, key=f"pos_{i}")
    if rider:
        selected_riders.append(rider)

# Afficher les pronostics
if len(selected_riders) == 20:
    st.success("Your pronostic is complete !")
    st.write("**Your top20:**")
    for i, rider in enumerate(selected_riders, start=1):
        st.write(f"{i}. {rider}")

selected_df = startlist.loc[startlist['Rider'].isin(selected_riders)]

def PL(startlist=selected_df):
    points_grille = [60, 35, 30, 26, 23, 20, 18, 16, 14, 12, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    
    # Convertir les colonnes nécessaires en numérique
    startlist['Price'] = pd.to_numeric(startlist['Price'], errors='coerce')
    
    # Création du problème de maximisation
    prob = LpProblem("Meilleure_Equipe", LpMaximize)
    
    # Variables de décision
    x = LpVariable.dicts("Coureur", startlist['Rider'], cat='Binary')
    
    # Fonction objectif : maximiser les points
    prob += lpSum([x[coureur] * points_grille[i] for i, coureur in enumerate(startlist['Rider']) if i < len(points_grille)])
    
    # Contraintes
    # 1. Prix total doit être inférieur ou égal à 5000
    prob += lpSum([x[coureur] * startlist['Price'].iloc[i] for i, coureur in enumerate(startlist['Rider'])]) <= 5000
    
    # 2. Nombre total de coureurs doit être égal à 9
    prob += lpSum([x[coureur] for coureur in startlist['Rider']]) == 9
    
    # Résolution du problème
    prob.solve()
    
    selected_coureurs_df = startlist[startlist['Rider'].isin([v.name.split("_")[1] for v in prob.variables() if v.varValue == 1])]
    result = []
    for pos in list(selected_coureurs_df.index):
        if pos < 20:
            result.append(points_grille[pos])
    
    # Calcul des totaux
    total_price = selected_coureurs_df['Price'].sum()
    total_points = sum(result)
    return selected_coureurs_df, total_price, total_points

df, total_price, total_points = PL()

st.header("Your table of results")
st.dataframe(selected_df, hide_index=True)
st.text(f"total_price : {total_price}")
st.text(f"total_points : {total_points}")