from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
# --- IMPORTS .ENV ---
from dotenv import load_dotenv
load_dotenv() 


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("⚠️ DATABASE_URL introuvable. Vérifie ton fichier .env !")

# Création du moteur de connexion
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Création de la fabrique de sessions (pour parler à la BDD à chaque requête)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour créer nos futures tables (Modèles ORM)
Base = declarative_base()

# Fonction utilitaire pour injecter la session BDD dans nos routes FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()