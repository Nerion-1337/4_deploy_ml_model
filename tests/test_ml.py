import os
import joblib
import pandas as pd
import numpy as np
# Preprocessing
from app.preprocessing.clean_and_onehot import pipeline_preprocessing

# --- Chemins vers fichiers ML ---
MODEL_ENERGY_PATH = "app/ml/model_energy.pkl"
MODEL_EMISSIONS_PATH = "app/ml/model_emissions.pkl"
SCALER_PATH = "app/ml/scaler.pkl"
# ---------------------------------------------

def test_model_files_exist():
    """Vérifie que les 3 fichiers binaires sont bien présents."""
    assert os.path.exists(MODEL_ENERGY_PATH), f"Modèle Énergie introuvable : {MODEL_ENERGY_PATH}"
    assert os.path.exists(MODEL_EMISSIONS_PATH), f"Modèle CO2 introuvable : {MODEL_EMISSIONS_PATH}"
    assert os.path.exists(SCALER_PATH), f"Scaler introuvable : {SCALER_PATH}"


def test_model_inference():
    """Vérifie la pipeline Data Science (Preprocessing -> Scaler -> Predict)."""
    # 1. Chargement des modèles
    try:
        model_energy = joblib.load(MODEL_ENERGY_PATH)
        model_emissions = joblib.load(MODEL_EMISSIONS_PATH)
        scaler = joblib.load(SCALER_PATH)
    except Exception as e:
        assert False, f"Erreur lors du chargement des fichiers : {e}"

    # 2. Donnée brute (Format dictionnaire, comme ce que fait features.model_dump())
    raw_data = {
        "YearBuilt": 2015,
        "NumberofBuildings": 1,
        "NumberofFloors": 5,
        "PropertyGFATotal": 150000.0,
        "PropertyGFAParking": 20000.0,
        "PropertyGFABuilding(s)": 130000.0,
        "PrimaryPropertyType": "Large Office",
        "LargestPropertyUseType": "Office",
        "LargestPropertyUseTypeGFA": 100000.0,
        "SecondLargestPropertyUseType": "Parking",
        "SecondLargestPropertyUseTypeGFA": 30000.0,
        "ThirdLargestPropertyUseType": "Aucun",
        "ThirdLargestPropertyUseTypeGFA": 0.0,
        "Neighborhood": "DOWNTOWN",
        "Latitude": 47.6062,
        "Longitude": -122.3321,
        "Has_Electricity": True,
        "Has_NaturalGas": False
    }

    try:
        # 3. Étape 1 : Preprocessing maison
        df_processed = pipeline_preprocessing(raw_data, scaler.feature_names_in_)
        
        # 4. Étape 2 : Scaler
        data_scaled = scaler.transform(df_processed)
        df_final = pd.DataFrame(data_scaled, columns=df_processed.columns)
        
        # 5. Étape 3 : Prédiction brute (Log)
        pred_energy_log = model_energy.predict(df_final)[0]
        pred_emissions_log = model_emissions.predict(df_final)[0]
        
        # 6. Étape 4 : Conversion exponentielle
        energie_finale = float(max(0.0, np.expm1(pred_energy_log)))
        emissions_finales = float(max(0.0, np.expm1(pred_emissions_log)))
        
    except Exception as e:
        assert False, f"La pipeline ML a planté : {e}"

    # 7. Vérifications finales (Tests métiers)
    assert energie_finale >= 0, "L'énergie prédite ne peut pas être négative."
    assert emissions_finales >= 0, "Les émissions de CO2 ne peuvent pas être négatives."