from pydantic import BaseModel, Field
from typing import Optional
# --- IMPORTS SQL ---
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

# ==========================================
# 1. MODÈLES PYDANTIC (Validation de l'API)
# ==========================================
class BuildingFeatures(BaseModel):
    # --- Caractéristiques physiques de base ---
    YearBuilt: int = Field(..., example=1980, description="Année de construction (sert à calculer l'Âge)")
    NumberofBuildings: int = Field(..., example=1, description="Nombre de bâtiments")
    NumberofFloors: int = Field(..., example=5, description="Nombre d'étages")
    
    # --- Coordonnées spatiales ---
    Latitude: float = Field(..., example=47.6062, description="Latitude du bâtiment")
    Longitude: float = Field(..., example=-122.3321, description="Longitude du bâtiment")
    
    # --- Surfaces Brutes (GFA) ---
    PropertyGFATotal: float = Field(..., example=120000.0, description="Surface totale brute (doit être > 0)")
    PropertyGFAParking: float = Field(..., example=20000.0, description="Surface allouée au parking")
    
    # Gestion de la colonne avec parenthèses via un alias Pydantic
    PropertyGFABuildings: float = Field(..., alias="PropertyGFABuilding(s)", example=100000.0, description="Surface des bâtiments")

    # --- Activités et Surfaces Détaillées (pour les Ratios) ---
    PrimaryPropertyType: str = Field(..., example="Large Office", description="Usage principal précis")
    LargestPropertyUseType: str = Field(..., example="Office", description="Activité dominante")
    LargestPropertyUseTypeGFA: float = Field(..., example=90000.0, description="Surface de l'activité dominante")
    
    SecondLargestPropertyUseType: Optional[str] = Field("Aucun", example="Parking", description="Activité annexe")
    SecondLargestPropertyUseTypeGFA: Optional[float] = Field(0.0, example=20000.0, description="Surface de l'activité annexe")
    
    ThirdLargestPropertyUseType: Optional[str] = Field("Aucun", example="Aucun", description="Troisième activité")
    ThirdLargestPropertyUseTypeGFA: Optional[float] = Field(0.0, example=0.0, description="Surface de la troisième activité")

    # --- Localisation & Systèmes Énergétiques ---
    Neighborhood: str = Field(..., example="DOWNTOWN", description="Nom du quartier pour le One-Hot Encoding")
    Has_Electricity: bool = Field(True, example=True, description="Le bâtiment utilise-t-il l'électricité ?")
    Has_NaturalGas: bool = Field(False, example=False, description="Le bâtiment utilise-t-il le gaz naturel ?")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "YearBuilt": 1995,
                "NumberofBuildings": 1,
                "NumberofFloors": 4,
                "Latitude": 47.6100,
                "Longitude": -122.3400,
                "PropertyGFATotal": 150000.0,
                "PropertyGFAParking": 30000.0,
                "PropertyGFABuilding(s)": 120000.0,
                "PrimaryPropertyType": "Commercial",
                "LargestPropertyUseType": "Retail Store",
                "LargestPropertyUseTypeGFA": 100000.0,
                "SecondLargestPropertyUseType": "Parking",
                "SecondLargestPropertyUseTypeGFA": 30000.0,
                "ThirdLargestPropertyUseType": "Aucun",
                "ThirdLargestPropertyUseTypeGFA": 0.0,
                "Neighborhood": "DOWNTOWN",
                "Has_Electricity": True,
                "Has_NaturalGas": True
            }
        }

class PredictionResponse(BaseModel):
    # Les deux cibles que ton modèle Futurisys doit prédire
    SiteEnergyUse_kBtu: float = Field(..., description="Consommation énergétique totale prédite (kBtu)")
    TotalGHGEmissions: float = Field(..., description="Émissions de gaz à effet de serre prédites (tonnes de CO2e)")
    
# ==========================================
# MODÈLE SQLALCHEMY (Structure de la BDD)
# ==========================================
class PredictionHistory(Base):
    # Nom de la table dans PostgreSQL
    __tablename__ = "predictions_history"

    # Clé primaire auto-incrémentée
    id = Column(Integer, primary_key=True, index=True)
    
    # Horodatage automatique de la requête
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Quelques données d'entrée pertinentes à conserver pour l'analyse
    YearBuilt = Column(Integer)
    PropertyGFATotal = Column(Float)
    PrimaryPropertyType = Column(String)
    Neighborhood = Column(String)
    
    # Les prédictions générées par ton modèle
    predicted_energy_kbtu = Column(Float)
    predicted_emissions_co2 = Column(Float)