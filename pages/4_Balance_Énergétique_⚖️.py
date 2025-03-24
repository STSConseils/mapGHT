import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium import Choropleth
from streamlit_folium import st_folium
from shapely.geometry import Point
import numpy as np
import branca.colormap as cm

# Configuration de la page Streamlit
st.set_page_config(layout="wide")
st.title("Carte de la balance énergétique par canton")
st.markdown("<h3 style='font-size:20px;'>La balance énergétique (en GWh) représente la différence de disponibilité entre les solvants usagés (flux 04) et les eaux solvantées (flux 01) pour atteindre un mix d'une valeur moyenne de 18 MJ/Kg. Cette différence caractérise le potentiel cantonal d'absorption des flux à faible PCI.</h3>", unsafe_allow_html=True)

# Chemins des fichiers
csv_file = "data/Balances_Ener_01_04.csv"
geojson_file = "data/cantons.geojson"

# Lecture du CSV avec les bonnes conversions
df_balance = pd.read_csv(csv_file, sep=";", decimal=",", engine="python")
df_balance["Cantons"] = df_balance["Cantons"].astype(str)
df_balance["Balance_Ener [GWh]"] = pd.to_numeric(df_balance["Balance_Ener [GWh]"], errors="coerce")

# Lecture du fichier GeoJSON
gdf = gpd.read_file(geojson_file)
gdf["id"] = gdf["id"].astype(str)

# Fusion des données
gdf = gdf.merge(
    df_balance[["Cantons", "Balance_Ener [GWh]"]],
    left_on="id", right_on="Cantons", how="left"
)

# Définition des seuils fixes pour les classes
seuils = {
    "Fortement déficitaire": (-float('inf'), -6),
    "Moyennement déficitaire": (-6, -3),
    "Faiblement déficitaire": (-3, 0),
    "Faiblement excédentaire": (0, 3),
    "Moyennement excédentaire": (3, 6),
    "Fortement excédentaire": (6, float('inf'))
}

# Fonction pour déterminer la classe de balance
def get_balance_class(value):
    if pd.isna(value):
        return "Pas d'installation d'incinération"
    for classe, (min_val, max_val) in seuils.items():
        if min_val <= value < max_val or (classe == "Fortement excédentaire" and value >= max_val):
            return classe
    return "Pas d'installation d'incinération"

# Création de la carte Folium
m = folium.Map(location=[46.8182, 8.2275], zoom_start=8, tiles="CartoDB positron")

# Création des couleurs pour les classes
class_colors = {
    "Fortement déficitaire": '#d73027',
    "Moyennement déficitaire": '#fc8d59',
    "Faiblement déficitaire": '#fee090',
    "Faiblement excédentaire": '#e0f3f8',
    "Moyennement excédentaire": '#91bfdb',
    "Fortement excédentaire": '#4575b4',
    "Pas d'installation d'incinération": '#ffffff'
}

# Style function pour la couche GeoJSON
def style_function(feature):
    canton_id = feature['properties']['id']
    canton_data = gdf[gdf['id'] == canton_id]
    if canton_data.empty or pd.isna(canton_data.iloc[0]['Balance_Ener [GWh]']):
        return {
            'fillColor': '#ffffff',
            'fillOpacity': 0.6,
            'color': 'black',
            'weight': 1
        }
    value = canton_data.iloc[0]['Balance_Ener [GWh]']
    balance_class = get_balance_class(value)
    return {
        'fillColor': class_colors[balance_class],
        'fillOpacity': 0.6,
        'color': 'black',
        'weight': 1
    }

# Ajouter la couche GeoJSON avec style et tooltip
folium.GeoJson(
    gdf.to_json(),
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["id", "Balance_Ener [GWh]"],
        aliases=["Canton:", "Balance (GWh):"],
        localize=True
    )
).add_to(m)

# Zone de recherche manuelle d'un canton
selected_canton = st.text_input("🔎 Rechercher un canton (ou cliquez sur la carte) :", "")

# Organiser l'affichage en deux colonnes
col1, col2 = st.columns([2, 1])

with col1:
    # Affichage de la carte et récupération des données de clic
    map_data = st_folium(m, width=900, height=600)

    if map_data and "last_clicked" in map_data and map_data["last_clicked"]:
        click_info = map_data["last_clicked"]
        click_lat = click_info.get("lat")
        click_lng = click_info.get("lng")
        if click_lat is not None and click_lng is not None:
            click_point = Point(click_lng, click_lat)
            buffer_radius = 0.01
            clicked = gdf[gdf.geometry.intersects(click_point.buffer(buffer_radius))]
            if not clicked.empty:
                selected_canton = clicked.iloc[0]["id"]

with col2:
    if selected_canton and selected_canton in gdf["id"].values:
        canton_data = gdf[gdf["id"] == selected_canton].iloc[0]
        balance = canton_data["Balance_Ener [GWh]"]
        balance_class = get_balance_class(balance)
        
        st.write("---")
        st.markdown(f"### {selected_canton}")
        if pd.isna(balance):
            st.markdown("**Pas d'installation d'incinération**")
        else:
            st.markdown(f"**{balance:.2f} GWh**")
            st.markdown(f"*{balance_class}*")
        st.write("---")
    else:
        st.info("Cliquez sur un canton sur la carte ou utilisez la recherche pour voir sa balance énergétique.")
    
    # Ajout de la légende dans la colonne 2
    st.markdown("### Légende")
    
    # Ordre des classes pour la légende
    ordered_classes = [
        "Fortement excédentaire",
        "Moyennement excédentaire",
        "Faiblement excédentaire",
        "Faiblement déficitaire",
        "Moyennement déficitaire",
        "Fortement déficitaire",
        "Pas d'installation d'incinération"
    ]

    # Création de la légende avec des colonnes pour chaque élément
    for label in ordered_classes:
        col_color, col_text = st.columns([1, 4])
        with col_color:
            st.markdown(
                f"""
                <div style="
                    background-color: {class_colors[label]};
                    border: 1px solid black;
                    width: 30px;
                    height: 20px;
                    margin: 5px 0;">
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_text:
            if label == "Pas d'installation d'incinération":
                st.markdown(f"{label}")
            else:
                min_val, max_val = seuils[label]
                if label == "Fortement excédentaire":
                    range_text = "≥ 6"
                elif label == "Fortement déficitaire":
                    range_text = "< -6"
                else:
                    range_text = f"[{min_val}, {max_val}["
                st.markdown(f"{label} ({range_text} GWh)") 