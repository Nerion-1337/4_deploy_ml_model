import pandas as pd
import numpy as np
import joblib
import os
from fastapi import FastAPI, HTTPException
from app.models import BuildingFeatures, PredictionResponse
# --- IMPORTS MODULE ---
from app.preprocessing.clean_and_onehot import pipeline_preprocessing


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

@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(features: BuildingFeatures):
    if model_energy is None or model_emissions is None or scaler is None:
        raise HTTPException(status_code=503, detail="Modèles non initialisés sur le serveur.")
    
    try:
        # ÉTAPE A : Extraction des données brutes
        raw_data = features.model_dump(by_alias=True)
        
        # ÉTAPE B : Pipeline de Feature Engineering commun
        # On passe la liste des caractéristiques apprises par le scaler
        df_processed = pipeline_preprocessing(raw_data, scaler.feature_names_in_)
        
        # ÉTAPE C : Mise à l'échelle (StandardScaler)
        data_scaled = scaler.transform(df_processed)
        df_final = pd.DataFrame(data_scaled, columns=df_processed.columns)
        
        # ÉTAPE D : Inférences parallèles sur les deux modèles distincts
        pred_energy_log = model_energy.predict(df_final)[0]
        pred_emissions_log = model_emissions.predict(df_final)[0]
        
        # ÉTAPE E : Transformation inverse (Rebasculement de l'échelle Log vers Réelle)
        energie_finale = np.expm1(pred_energy_log)
        emissions_finales = np.expm1(pred_emissions_log)
        
        return PredictionResponse(
            SiteEnergyUse_kBtu=max(0.0, energie_finale),
            TotalGHGEmissions=max(0.0, emissions_finales)
        )
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors du calcul : {str(e)}")