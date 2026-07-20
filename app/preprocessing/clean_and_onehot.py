import pandas as pd

def pipeline_preprocessing(raw_data: dict, expected_columns: list) -> pd.DataFrame:
    """
    Prend les données brutes d'une requête (sous forme de dictionnaire) 
    et applique l'intégralité du pipeline de Feature Engineering avancé.
    Renvoie un DataFrame Pandas aligné sur les colonnes du modèle ML.
    """
    # 1. Conversion du dictionnaire en DataFrame (1 ligne)
    df = pd.DataFrame([raw_data])
    
    # 2. Transformation de l'année en Âge du bâtiment
    df['BuildingAge'] = 2016 - df['YearBuilt']
    
    # 3. Création des Ratios d'allocation de surface (Sécurisé contre la division par 0)
    gfa_total = df['PropertyGFATotal'].iloc[0]
    if gfa_total > 0:
        df['Ratio_Parking'] = df['PropertyGFAParking'] / gfa_total
        df['Ratio_LargestUse'] = df['LargestPropertyUseTypeGFA'] / gfa_total
        df['Ratio_SecondUse'] = df['SecondLargestPropertyUseTypeGFA'] / gfa_total
        df['Ratio_ThirdUse'] = df['ThirdLargestPropertyUseTypeGFA'] / gfa_total
    else:
        df['Ratio_Parking'] = df['Ratio_LargestUse'] = df['Ratio_SecondUse'] = df['Ratio_ThirdUse'] = 0.0

    # 4. Multi-Hot Encoding des activités pour CE bâtiment spécifique
    row_activities = [
        df['PrimaryPropertyType'].iloc[0],
        df['LargestPropertyUseType'].iloc[0],
        df['SecondLargestPropertyUseType'].iloc[0],
        df['ThirdLargestPropertyUseType'].iloc[0]
    ]
    
    # Nettoyage de la liste (on ignore 'Aucun' et les valeurs manquantes)
    row_activities = set([act for act in row_activities if act != 'Aucun' and pd.notna(act)])
    
    # On active à 1 les colonnes d'activités présentes
    for act in row_activities:
        nom_colonne = f"Use_{act.replace(' ', '_').replace('/', '_')}"
        df[nom_colonne] = 1
        
    # 5. One-Hot Encoding du Quartier (Neighborhood)
    df = pd.get_dummies(df, columns=['Neighborhood'], prefix=['Neigh'], dtype=int)
    
    # 6. ALIGNEMENT DES COLONNES (L'astuce de conformité)
    # On force le DataFrame à posséder exactement les colonnes apprises à l'entraînement
    df_final = df.reindex(columns=expected_columns, fill_value=0)
    
    return df_final