import requests
import pandas as pd

# Fonction pour obtenir les métadonnées des jeux de données de transport
def get_transport_datasets_metadata():
    base_url = 'https://mobilithek.info/mobilithek/api/v1.0/export/datasets/dcatapde'
    headers = {
        'Accept': 'application/ld+json'
    }
    params = {
        'categories': 'https://w3id.org/mdp/schema/data_categories#PUBLIC_TRANSPORT_SCHEDULED_TRANSPORT,'
                      'https://w3id.org/mdp/schema/data_categories#PUBLIC_TRANSPORT_NONSCHEDULED_TRANSPORT,'
                      'https://w3id.org/mdp/schema/data_categories#CAR_UND_BIKE_SHARING,'
                      'https://w3id.org/mdp/schema/data_categories#CYCLE_NETWORK_DATA,'
                      'https://w3id.org/mdp/schema/data_categories#AIR_AND_SPACE_TRAVEL,'
                      'https://w3id.org/mdp/schema/data_categories#RAILWAY',
        'size': 20  # Nombre maximum de résultats par page (20)
    }

    all_datasets = []
    page = 0
    while True:
        params['page'] = page
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()  # Vérifier que la requête a réussi

        data = response.json()
        print(f"Page {page} response JSON: {data}")  # Débogage: imprimer la réponse JSON complète

        # Vérifiez la structure de la réponse JSON
        if '@graph' in data:
            datasets = data['@graph']  # Extraire les datasets à partir de '@graph'
        else:
            print(f"Clé de datasets non trouvée dans la réponse JSON à la page {page}.")
            break

        if not datasets:
            break

        all_datasets.extend(datasets)
        page += 1
        if len(all_datasets) >= 546:
            break

    return all_datasets

# Récupérer les métadonnées et les stocker dans un DataFrame
datasets_metadata = get_transport_datasets_metadata()
df = pd.DataFrame(datasets_metadata)

# Afficher les premières lignes du DataFrame
print(df.head())
df.to_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/germany.xlsx', index=False)
