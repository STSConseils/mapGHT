import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import plotly.express as px
from folium import Choropleth
from streamlit_folium import st_folium
from shapely.geometry import Point


# 📌 Configuration de la page Streamlit
st.set_page_config(layout="wide")
st.title("Carte du potentiel énergétique total par canton")
st.markdown("<h3 style='font-size:20px;'>Le potentiel énergétique résiduel (en GWh) correspond à la valorisation des flux restants après optimisation du PCI moyen à 18 MJ/Kg </h3>", unsafe_allow_html=True)


# 📌 Chemins des fichiers
csv_file = "data/Potentiel_Ener_Res_GWh.csv"
geojson_file = "data/cantons.geojson"

# 📌 Lecture du CSV avec les bonnes conversions
df_potentiel = pd.read_csv(csv_file, sep=";", decimal=",", engine="python")

# Conversion des colonnes énergétiques en float
cols_energy = ["Pot_Ener_01 [GWh]", "Pot_Ener_04 [GWh]", "Pot_Ener_08 [GWh]", "Pot_Ener_11 [GWh]", "Pot_Ener [GWh]"]
for col in cols_energy:
    df_potentiel[col] = pd.to_numeric(df_potentiel[col], errors="coerce").fillna(0)
df_potentiel["Cantons"] = df_potentiel["Cantons"].astype(str)

# 📌 Lecture du fichier GeoJSON
gdf = gpd.read_file(geojson_file)
gdf["id"] = gdf["id"].astype(str)

# 📌 Pour la carte choroplèthe, on fusionne uniquement la valeur globale depuis le CSV
gdf = gdf.merge(
    df_potentiel[["Cantons", "Pot_Ener [GWh]"]],
    left_on="id", right_on="Cantons", how="left"
)
gdf.fillna(0, inplace=True)

# 📌 Définition des seuils pour la choroplèthe
bins = [0, 5,10,15,20,25, 30, 35, 40]

# 📌 Création de la carte Folium
m = folium.Map(location=[46.8182, 8.2275], zoom_start=8, tiles="CartoDB positron")

# Ajouter la couche choroplèthe
Choropleth(
    geo_data=gdf.to_json(),
    data=gdf,
    columns=["id", "Pot_Ener [GWh]"],
    key_on="feature.properties.id",
    fill_color="YlOrRd",
    fill_opacity=0.6,
    line_opacity=0.3,
    bins=bins,
    legend_name="Potentiel Énergétique (GWh)"
).add_to(m)

# Ajouter la couche GeoJSON avec tooltip sans style visible (pour supprimer la surcouche bleue)
folium.GeoJson(
    gdf.to_json(),
    name="Cantons",
    style_function=lambda feature: {'fillOpacity': 0, 'weight': 0},
    tooltip=folium.GeoJsonTooltip(fields=["id"], aliases=["Canton:"])
).add_to(m)

# 📌 Zone de recherche manuelle d'un canton
selected_canton = st.text_input("🔎 Rechercher un canton (ou cliquez sur la carte) :", "")

# Organiser l'affichage en deux colonnes : carte à gauche, graphique à droite
col1, col2 = st.columns([2, 1])

with col1:
    # 📌 Affichage de la carte et récupération des données de clic
    map_data = st_folium(m, width=900, height=600)

    # 📌 Si un clic a été effectué, utiliser ses coordonnées pour déterminer le canton cliqué
    if map_data and "last_clicked" in map_data and map_data["last_clicked"]:
        click_info = map_data["last_clicked"]
        st.write("Données du dernier clic :", click_info)  # Debug
        click_lat = click_info.get("lat")
        click_lng = click_info.get("lng")
        if click_lat is not None and click_lng is not None:
            click_point = Point(click_lng, click_lat)  # (longitude, latitude)
            # Utiliser un buffer pour capter les clics proches des limites
            buffer_radius = 0.01  # environ 1 km en degrés
            clicked = gdf[gdf.geometry.intersects(click_point.buffer(buffer_radius))]
            if not clicked.empty:
                selected_canton = clicked.iloc[0]["id"]
            else:
                st.warning("Aucun canton trouvé pour le clic.")

with col2:
    # 📌 Affichage du Pie Chart si un canton est sélectionné et trouvé dans le CSV
    if selected_canton and selected_canton in df_potentiel["Cantons"].values:
        # Filtrer le CSV pour le canton sélectionné
        canton_data = df_potentiel[df_potentiel["Cantons"] == selected_canton].iloc[0]
        
        # Récupérer les valeurs des flux énergétiques
        energy_values = {
            "Solvants usagés": canton_data["Pot_Ener_01 [GWh]"],
            "Eaux solvantées": canton_data["Pot_Ener_04 [GWh]"],
            "Boues industrielles": canton_data["Pot_Ener_08 [GWh]"],
            "Émulsions": canton_data["Pot_Ener_11 [GWh]"]
        }
        
        # Calcul du potentiel total
        potentiel_total = sum(energy_values.values())
        
        # Création du Pie Chart avec Plotly
        fig = px.pie(
            names=list(energy_values.keys()),
            values=list(energy_values.values()),
            title=f"Composition du Potentiel Énergétique de {selected_canton}",
            hole=0.3
        )
        # Ajuster le layout pour laisser de l'espace pour le titre
        fig.update_layout(
            title={'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
            margin=dict(t=100, b=50, l=50, r=50)
        )
        fig.update_traces(textinfo="percent+label", hoverinfo="label+value")
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"**Potentiel cantonal : {potentiel_total:.2f} GWh**")
    else:
        st.info("Cliquez sur un canton sur la carte ou utilisez la recherche pour sélectionner un canton.")
