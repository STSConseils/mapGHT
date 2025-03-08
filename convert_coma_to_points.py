import pandas as pd

# Nom du fichier original
input_file = "/Users/lolevray/Documents/Consulting/TreaTech/Data/GIS/Couches_csv/Companies_geocoded_all_unique.csv"
# Nom du fichier corrigé
output_file = "/Users/lolevray/Documents/Consulting/TreaTech/Data/GIS/Couches_csv/Companies_geocoded_all_unique_corrected.csv"

try:
    # Essayer d'ouvrir avec une virgule comme séparateur
    df = pd.read_csv(input_file, sep=",")
except pd.errors.ParserError:
    # Si erreur, essayer avec un point-virgule
    df = pd.read_csv(input_file, sep=";")

# Vérifier si les colonnes latitude et longitude existent
if "latitude" in df.columns and "longitude" in df.columns:
    # Remplacer les virgules par des points et convertir en float
    df["latitude"] = df["latitude"].str.replace(",", ".").astype(float)
    df["longitude"] = df["longitude"].str.replace(",", ".").astype(float)
    
    # Sauvegarder le fichier corrigé
    df.to_csv(output_file, index=False)

    print(f"✅ Fichier corrigé enregistré sous : {output_file}")
else:
    print("❌ Erreur : Colonnes 'latitude' et 'longitude' non trouvées dans le fichier.")