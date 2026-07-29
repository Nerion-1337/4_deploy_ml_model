import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Charger les variables d'environnement (pour se connecter à la DB locale)
load_dotenv()

# Connexion à la base de données
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "super_password_123")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "futurisys_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# Chemin vers ton jeu de données initial (à modifier si besoin)
DATASET_PATH = "data/cleaned_building_data.parquet" 

def load_data_to_db():
    print(f"Chargement du dataset depuis {DATASET_PATH}...")
    try:
        # Lire le fichier (adapte le séparateur si c'est un point-virgule)
        df = pd.read_parquet(DATASET_PATH)
        
        # Envoyer les données dans une nouvelle table 'initial_dataset'
        # if_exists='replace' permet de recréer la table si tu relances le script
        df.to_sql("initial_dataset", engine, if_exists="replace", index=False)
        
        print(f"✅ Succès ! {len(df)} lignes ont été insérées dans la table 'initial_dataset'.")
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion : {e}")

if __name__ == "__main__":
    load_data_to_db()