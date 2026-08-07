import pandas as pd
import numpy as np
import joblib
import os
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
# --- IMPORTS MODULE ---
from app.preprocessing.clean_and_onehot import pipeline_preprocessing
from app.models import BuildingFeatures, PredictionResponse, BuildingInputDB, PredictionResultDB
from app.database import engine, get_db, Base

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
@app.post("/predict", response_model=PredictionResponse)
def predict(features: BuildingFeatures, db: Session = Depends(get_db)):
    
    # 1. On récupère la liste des colonnes mémorisées par le scaler
    colonnes_attendues = scaler.feature_names_in_
    
    # 2. 🚨 CRUCIAL : On transforme l'objet Pydantic en DataFrame Pandas (1 ligne)
    df_brut = pd.DataFrame([features.model_dump(by_alias=True)])
    
    # 3. Feature Engineering (On donne bien le DataFrame, pas l'objet Pydantic)
    raw_data = features.model_dump(by_alias=True)
    df_transformed = pipeline_preprocessing(raw_data, expected_columns=colonnes_attendues)
    
    # 4. Mise à l'échelle (Scaling)
    X_scaled = scaler.transform(df_transformed)

    # 5. Prédictions
    energy_pred = model_energy.predict(X_scaled)[0]
    co2_pred = model_emissions.predict(X_scaled)[0]

    # 5. Sauvegarde dans la Table 1 (Les entrées)
    db_input = BuildingInputDB(
        year_built=features.YearBuilt,
        number_of_buildings=features.NumberofBuildings,
        number_of_floors=features.NumberofFloors,
        latitude=features.Latitude,
        longitude=features.Longitude,
        property_gfa_total=features.PropertyGFATotal,
        property_gfa_parking=features.PropertyGFAParking,
        property_gfa_buildings=features.PropertyGFABuildings,
        primary_property_type=features.PrimaryPropertyType,
        largest_property_use_type=features.LargestPropertyUseType,
        largest_property_use_type_gfa=features.LargestPropertyUseTypeGFA,
        neighborhood=features.Neighborhood,
        has_electricity=features.Has_Electricity,
        has_natural_gas=features.Has_NaturalGas
    )
    db.add(db_input)
    db.commit()
    db.refresh(db_input) 

    # 6. Sauvegarde dans la Table 2 (Les sorties avec Clé Étrangère)
    db_prediction = PredictionResultDB(
        building_input_id=db_input.id,
        predicted_energy_kbtu=float(energy_pred),
        predicted_emissions_co2=float(co2_pred)
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)

    # 7. Retour de la réponse finale
    return PredictionResponse(
        prediction_id=db_prediction.id,
        building_input_id=db_input.id,
        SiteEnergyUse_kBtu=energy_pred,
        TotalGHGEmissions=co2_pred
    )