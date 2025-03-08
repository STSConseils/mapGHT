import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 📌 Titre de l'application
st.title("Carte interactive des entreprises en Suisse")

# 📌 Charger le fichier corrigé
csv_file = "/Users/lolevray/Documents/Consulting/TreaTech/Data/GIS/Couches_csv/Companies_geocoded_all_unique_corrected.csv"
df = pd.read_csv(csv_file)

# 📌 Vérifier les colonnes nécessaires
if {"latitude", "longitude", "Group", "Cantons"}.issubset(df.columns):

    # 🟢 Définition des couleurs et tailles selon "Group"
    color_map = {"Remettantes": "green", "Incinération": "red", "Regroupement": "blue"}
    size_map = {"Remettantes": 2, "Incinération": 8, "Regroupement": 4}

    # 🎯 Ajouter des filtres interactifs
    selected_canton = st.selectbox("Sélectionnez un canton :", ["Tous"] + sorted(df["Cantons"].unique()))
    selected_group = st.multiselect("Filtrer par type d'entreprise :", df["Group"].unique(), default=df["Group"].unique())

    # 📌 Appliquer les filtres
    filtered_df = df[df["Group"].isin(selected_group)]
    if selected_canton != "Tous":
        filtered_df = filtered_df[filtered_df["Cantons"] == selected_canton]

    # 🗺️ Création de la carte avec un fond sombre en niveaux de gris
    m = folium.Map(
        location=[46.8182, 8.2275], 
        zoom_start=8, 
        tiles="CartoDB positron",
        attr='© OpenStreetMap contributors, © CartoDB'
    )

    # 📌 Ajouter les points en tant que cercles de couleurs et tailles différentes
    for _, row in filtered_df.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=size_map.get(row["Group"], 5),  # Taille du cercle
            color=color_map.get(row["Group"], "gray"),  # Bordure du cercle
            fill=True,
            fill_color=color_map.get(row["Group"], "gray"),  # Remplissage du cercle
            fill_opacity=0.6,
            popup=f"{row['Companies']} - {row['Cities']} ({row['Group']})"
        ).add_to(m)

    # 📌 Afficher la carte dans Streamlit
    st_folium(m, width=800, height=600)

else:
    st.error("Les colonnes nécessaires ('latitude', 'longitude', 'Group', 'Cantons') ne sont pas présentes dans le fichier CSV.")


