import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 📌 Configurer la largeur maximale de la page
st.set_page_config(layout="wide")

# 📌 Titre de l'application
st.title("Carte interactive des entreprises qui remettent, regroupent et éliminent des déchets spéciaux liquides en Suisse")
st.markdown("<h3 style='font-size:20px;'>Visualisez les entreprises par catégorie et exportez les données filtrées.</h3>", unsafe_allow_html=True)

# 📌 Charger le fichier corrigé
csv_file = "data/Companies_geocoded_all_unique_corrected.csv"
df = pd.read_csv(csv_file)

# 📌 Vérifier les colonnes nécessaires
if {"latitude", "longitude", "Group", "Cantons"}.issubset(df.columns):

    # 🟢 Définition des couleurs et tailles selon "Group"
    color_map = {"Remettantes": "green", "Incinération": "red", "Regroupement": "blue"}
    size_map = {"Remettantes": 2, "Incinération": 8, "Regroupement": 4}

    # 📌 Filtres côte à côte au-dessus de la carte
    st.subheader("Filtres")
    col_filters1, col_filters2 = st.columns(2)
    
    with col_filters1:
        selected_canton = st.selectbox("Sélectionnez un canton :", ["Tous"] + sorted(df["Cantons"].unique()))
    
    with col_filters2:
        selected_group = st.multiselect("Filtrer par type d'entreprise :", df["Group"].unique(), default=df["Group"].unique())

    # 📌 Appliquer les filtres aux données
    filtered_df = df[df["Group"].isin(selected_group)]
    if selected_canton != "Tous":
        filtered_df = filtered_df[filtered_df["Cantons"] == selected_canton]

    # Affichage des données brutes filtrées
    st.subheader("Données détaillées")
    st.dataframe(filtered_df, height=200)
    st.download_button(
        label="Télécharger les données",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_data.csv",
        mime="text/csv"
    )

    # 🗺️ Création de la carte avec un fond clair
    m = folium.Map(
        location=[46.8182, 8.2275], 
        zoom_start=8, 
        tiles="CartoDB positron",
        attr='© OpenStreetMap contributors, © CartoDB'
    )

    # 📌 Ajouter les points en tant que cercles colorés et redimensionnés
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

    # Affichage de la carte en pleine largeur
    st_folium(m, width=1400, height=650)

else:
    st.error("Les colonnes nécessaires ('latitude', 'longitude', 'Group', 'Cantons') ne sont pas présentes dans le fichier CSV.")




