import requests
import pandas as pd

# Fonction pour obtenir les métadonnées des jeux de données de transport de la Pologne
def get_poland_transport_datasets():
    base_url = 'https://api.dane.gov.pl/1.4/datasets'
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en'  # Pour obtenir les réponses en anglais
    }
    params = {
        'page': 1,
        'per_page': 20,
        'categories[id][terms]': 143  # Catégorie de transport
    }

    all_datasets = []

    while True:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()  # Vérifier que la requête a réussi

        data = response.json()
        #print(f"Page {params['page']} response JSON: {data}")  # Débogage: imprimer la réponse JSON complète

        # Extraire les jeux de données de la réponse JSON
        datasets = data.get('data', [])
        if not datasets:
            break

        all_datasets.extend(datasets)
        params['page'] += 1

        # Arrêter si tous les jeux de données sont récupérés
        if 'meta' in data and 'total_count' in data['meta']:
            total_count = data['meta']['total_count']
            if len(all_datasets) >= total_count:
                break

    return all_datasets

# Récupérer les métadonnées et les stocker dans un DataFrame
datasets_metadata = get_poland_transport_datasets()
df = pd.DataFrame(datasets_metadata)

# Ajouter les colonnes demandées
df['Score du dataset'] = df['attributes'].apply(lambda x: x.get('openness_scores', [None])[0])
df['Fréquence d\'actualisation'] = df['attributes'].apply(lambda x: x.get('update_frequency'))
df['Licence combinée'] = df['attributes'].apply(lambda x: x.get('license_name'))

# Afficher les premières lignes du DataFrame
#print(df.head())
df.to_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/poland_transport_datasets.xlsx', index=False)
