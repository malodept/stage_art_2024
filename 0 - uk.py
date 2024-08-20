import requests
import pandas as pd

# Fonction pour obtenir les métadonnées de tous les jeux de données de transport
def get_transport_datasets_metadata():
    # URL de base de l'API
    base_url = 'https://data.gov.uk/api/action/package_search'
    
    # Paramètres de la requête
    params = {
        'q': 'Transport',  # Thème des jeux de données
        'rows': 752  # Nombre de jeux de données à récupérer
    }
    
    # Effectuer la requête à l'API
    response = requests.get(base_url, params=params)
    response.raise_for_status()  # Vérifier que la requête a réussi
    
    # Récupérer les données au format JSON
    data = response.json()
    
    # Extraire les résultats (métadonnées des jeux de données)
    datasets = data['result']['results']
    
    # Créer une liste de dictionnaires pour les métadonnées
    metadata_list = []
    for dataset in datasets:
        metadata_list.append(dataset)
    
    # Créer un DataFrame à partir de la liste de dictionnaires
    df = pd.DataFrame(metadata_list)
    
    return df

# Obtenir les métadonnées des jeux de données de transport et les afficher
transport_datasets_df = get_transport_datasets_metadata()

transport_datasets_df.to_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/uk.xlsx', index=False)
