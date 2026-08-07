import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import BuildingInputDB, PredictionResultDB

# ---------------------------------------------------------
# 1. SETUP DE LA BASE DE DONNÉES DE TEST (FIXTURE)
# ---------------------------------------------------------

# On crée une base de données temporaire en mémoire (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Cette fixture crée les tables dans la BDD en mémoire avant chaque test,
    fournit la session (db), puis détruit tout à la fin du test.
    """
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    
    # Créer la session
    db = TestingSessionLocal()
    try:
        yield db  # C'est ici que la session est injectée dans le test
    finally:
        db.close()
        # Nettoyer les tables après le test
        Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------
# 2. LE TEST DE LA RELATION ENTRE LES DEUX TABLES
# ---------------------------------------------------------

def test_double_table_relation(db_session):
    """
    Vérifie l'insertion dans la Table 1, l'association par Clé Étrangère
    dans la Table 2 et la navigation ORM entre les deux.
    """
    # 1. Création d'une entrée dans Table 1 (BuildingInputDB)
    building_entry = BuildingInputDB(
        year_built=1995,
        number_of_buildings=1,
        number_of_floors=4,
        latitude=47.61,
        longitude=-122.34,
        property_gfa_total=150000.0,
        property_gfa_parking=30000.0,
        property_gfa_buildings=120000.0,
        primary_property_type="Commercial",
        largest_property_use_type="Retail Store",
        largest_property_use_type_gfa=100000.0,
        neighborhood="DOWNTOWN",
        has_electricity=True,
        has_natural_gas=True
    )
    db_session.add(building_entry)
    db_session.commit()
    db_session.refresh(building_entry)

    # On vérifie que la base a bien généré un ID
    assert building_entry.id is not None

    # 2. Création de la prédiction associée dans Table 2 (PredictionResultDB)
    prediction_entry = PredictionResultDB(
        building_input_id=building_entry.id,  # Liaison par Clé Étrangère !
        predicted_energy_kbtu=4500000.5,
        predicted_emissions_co2=120.8
    )
    db_session.add(prediction_entry)
    db_session.commit()
    db_session.refresh(prediction_entry)

    # 3. Vérifications de la Table 2
    assert prediction_entry.id is not None
    assert prediction_entry.building_input_id == building_entry.id

    # 4. Vérification de la relation ORM SQLAlchemy
    # On va chercher la prédiction en base...
    retrieved_prediction = db_session.query(PredictionResultDB).filter_by(id=prediction_entry.id).first()
    
    # ... et on vérifie qu'on peut remonter à la table parent (Table 1) via la relation !
    assert retrieved_prediction.building_input.neighborhood == "DOWNTOWN"
    assert len(building_entry.predictions) == 1
    assert building_entry.predictions[0].predicted_energy_kbtu == 4500000.5