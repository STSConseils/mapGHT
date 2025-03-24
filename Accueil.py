import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Bienvenue sur le Dashboard du projet **Potentiel de la GHT en Suisse**")

st.sidebar.success("Selectionnez une carte ci-dessus.")

# Injection du CSS pour ajuster l'espace en haut
st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        padding-top: 1rem;  /* Ajuste cette valeur selon tes besoins */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Puis ton markdown habituel
st.markdown(
    """
    Ce dashboard vous permet d'explorer les résultats géoréférencés du projet **La Gazéification Hydrothermale en Suisse : une alternative durable à l’incinération des déchets spéciaux liquides**.
    **👈 Selectionnez une carte dans la barre latérale** pour commencer à explorer les données!
    """,
    unsafe_allow_html=True
)
