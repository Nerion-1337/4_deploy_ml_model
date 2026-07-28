from fastapi.testclient import TestClient
from app.main import app

# Création du client de test (simule un navigateur/Postman)
client = TestClient(app)

def test_read_root():
    """
    Test de la route de santé de l'API (Health Check).
    Vérifie que l'API est en ligne et renvoie le bon message.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "L'API Multi-Modèles Futurisys est opérationnelle."}
    

def test_predict_valid_data():
    """
    Vérifie que la route /predict fonctionne avec des données correctes.
    """
    payload = {
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
    
    # L'utilisation de "with" force l'API à démarrer et à charger les modèles ML !
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
    
    # On vérifie que la requête a réussi (Code 200)
    assert response.status_code == 200
    
    # On vérifie que la réponse contient bien nos deux prédictions
    data = response.json()
    assert "SiteEnergyUse_kBtu" in data
    assert "TotalGHGEmissions" in data


def test_predict_invalid_data():
    """
    Vérifie que l'API rejette correctement les requêtes incomplètes (Erreur 422).
    """
    payload = {
        "YearBuilt": 2015
    }
    
    # Pareil ici, on utilise "with"
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
    
    assert response.status_code == 422