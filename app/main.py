import pandas as pd
import numpy as np
import joblib
import os
from fastapi import FastAPI, HTTPException, Depends
from app.models import BuildingFeatures, PredictionResponse, PredictionHistory
from app.database import engine, get_db, Base
from sqlalchemy.orm import Session
# --- IMPORTS MODULE ---
from app.preprocessing.clean_and_onehot import pipeline_preprocessing

# --- CRÉATION DE LA TABLE AUTOMATIQUE ---
# Si la table "predictions_history" n'existe pas, SQLAlchemy la crée tout seul !
Base.metadata.create_all(bind=engine)

# 1. Initialisation de l'application
app = FastAPI(
    title="API de Prédiction Multi-Modèles - Futurisys",
    description="API industrialisée avec modèles découplés pour l'Énergie et le CO2.",
    version="1.3.0"
)

# 2. Emplacements des fichiers binaires
MODEL_ENERGY_PATH = "app/ml/model_energy.pkl"
MODEL_EMISSIONS_PATH = "app/ml/model_emissions.pkl"
SCALER_PATH = "app/ml/scaler.pkl"

model_energy = None
model_emissions = None
scaler = None

@app.on_event("startup")
def load_ml_assets():
    global model_energy, model_emissions, scaler
    if os.path.exists(MODEL_ENERGY_PATH) and os.path.exists(MODEL_EMISSIONS_PATH) and os.path.exists(SCALER_PATH):
        model_energy = joblib.load(MODEL_ENERGY_PATH)
        model_emissions = joblib.load(MODEL_EMISSIONS_PATH)
        scaler = joblib.load(SCALER_PATH)
        print("✅ Tous les assets ML (Énergie, CO2, Scaler) sont chargés !")
    else:
        print("⚠️ Attention: L'un des modèles ou le Scaler est introuvable dans app/ml/")

@app.get("/", tags=["Health"])
def read_root():
    return {"message": "L'API Multi-Modèles Futurisys est opérationnelle."}
            
# --- ROUTE PREDICT MISE À JOUR AVEC SAUVEGARDE DB ---
# On ajoute "db: Session = Depends(get_db)" dans les paramètres
@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(features: BuildingFeatures, db: Session = Depends(get_db)):
    if model_energy is None or model_emissions is None or scaler is None:
        raise HTTPException(status_code=503, detail="Modèles non initialisés.")
    
    try:
        raw_data = features.model_dump(by_alias=True)
        
        # 1. Pipeline ML
        df_processed = pipeline_preprocessing(raw_data, scaler.feature_names_in_)
        data_scaled = scaler.transform(df_processed)
        df_final = pd.DataFrame(data_scaled, columns=df_processed.columns)
        
        # 2. Prédictions
        pred_energy_log = model_energy.predict(df_final)[0]
        pred_emissions_log = model_emissions.predict(df_final)[0]
        
        energie_finale = float(max(0.0, np.expm1(pred_energy_log)))
        emissions_finales = float(max(0.0, np.expm1(pred_emissions_log)))

        # ==========================================
        # 3. ENREGISTREMENT DANS LA BASE DE DONNÉES
        # ==========================================
        nouvelle_prediction = PredictionHistory(
            YearBuilt=features.YearBuilt,
            PropertyGFATotal=features.PropertyGFATotal,
            PrimaryPropertyType=features.PrimaryPropertyType,
            Neighborhood=features.Neighborhood,
            predicted_energy_kbtu=energie_finale,
            predicted_emissions_co2=emissions_finales
        )
        
        db.add(nouvelle_prediction) # On ajoute à la transaction
        db.commit()                 # On valide l'enregistrement
        # ==========================================

        return PredictionResponse(
            SiteEnergyUse_kBtu=energie_finale,
            TotalGHGEmissions=emissions_finales
        )
            
    except Exception as e:
        db.rollback() # En cas d'erreur, on annule l'écriture en base
        raise HTTPException(status_code=400, detail=f"Erreur : {str(e)}")