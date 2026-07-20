import pandas as pd
import joblib
import os
from fastapi import FastAPI, HTTPException
from app.models import BuildingFeatures, PredictionResponse
# --- IMPORTS MODULE ---
from app.preprocessing.clean_and_onehot import pipeline_preprocessing


# 1. Initialisation de l'application FastAPI
app = FastAPI(
    title="API de Prédiction Énergétique - Futurisys",
    description="API découplée et industrialisée pour la prédiction énergétique des bâtiments.",
    version="1.1.0"
)

# 2. Gestion du cycle de vie du modèle ML
MODEL_PATH = "app/ml/model.pkl"
model = None

@app.on_event("startup")
def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("✅ Modèle ML chargé avec succès !")
    else:
        print(f"⚠️ Attention: Modèle introuvable au chemin {MODEL_PATH}")

# 3. Route de santé (Health Check)
@app.get("/", tags=["Health"])
def read_root():
    return {"message": "L'API Futurisys est opérationnelle.", "version": "1.1.0"}

# 4. Route Principale de Prédiction
@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(features: BuildingFeatures):
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé sur le serveur.")
    
    try:
        # ÉTAPE A : Extraction des données Pydantic au format dictionnaire brut
        # by_alias=True conserve la clé exacte "PropertyGFABuilding(s)" requise par le preprocessing
        raw_data = features.model_dump(by_alias=True)
        
        # ÉTAPE B : Appel du pipeline de transformation externalisé
        # On lui passe la liste des colonnes cibles du modèle : model.feature_names_in_
        df_processed = pipeline_preprocessing(raw_data, model.feature_names_in_)
        
        # ÉTAPE C : Inférence par le modèle
        prediction = model.predict(df_processed)
        
        # ÉTAPE D : Formatage de la réponse HTTP
        if prediction.shape[1] == 2 if len(prediction.shape) > 1 else False:
            return PredictionResponse(
                SiteEnergyUse_kBtu=float(prediction[0][0]),
                TotalGHGEmissions=float(prediction[0][1])
            )
        else:
            return PredictionResponse(
                SiteEnergyUse_kBtu=float(prediction[0]),
                TotalGHGEmissions=0.0
            )
            
    except Exception as e:
        # En production, on loggue l'erreur en interne et on renvoie un code propre au client
        raise HTTPException(status_code=400, detail=f"Erreur de traitement des données : {str(e)}")