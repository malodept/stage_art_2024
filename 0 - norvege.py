import requests
import pandas as pd
import datetime

# Définir l'URL de base de l'API Mobility v2
base_url = "https://api.entur.io/mobility/v2/gbfs"
headers = {
    "ET-Client-Name": "malo_de_pastor"  
}

# Fonction pour récupérer la liste des systèmes (opérateurs) disponibles
def fetch_systems():
    response = requests.get(base_url, headers=headers)
    response.raise_for_status()
    return response.json()['systems']

# Fonction pour récupérer les métadonnées pour chaque système GBFS
def fetch_system_metadata(system_url):
    response = requests.get(system_url, headers=headers)
    response.raise_for_status()
    return response.json()

# Fonction pour convertir un timestamp Unix en une date et heure lisibles
def convert_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Collecte des métadonnées pour tous les opérateurs
systems = fetch_systems()
metadata_list = []

for system in systems:
    system_metadata = fetch_system_metadata(system['url'])
    data_feeds = system_metadata.get('data', {}).get('nb', {}).get('feeds', [])
    
    # Pour chaque feed, on récupère les informations supplémentaires
    for feed in data_feeds:
        # Récupérer les informations supplémentaires depuis le lien Feed URL
        feed_details = fetch_system_metadata(feed['url'])
        system_info = feed_details.get('data', {})

        metadata_list.append({
            "System ID": system['id'],
            "System URL": system['url'],
            "Feed Name": feed['name'],
            "Feed URL": feed['url'],
            "System Name": system_info.get('name', 'N/A'),
            "Operator": system_info.get('operator', 'N/A'),
            "Phone Number": system_info.get('phone_number', 'N/A'),
            "Email": system_info.get('email', 'N/A'),
            "Timezone": system_info.get('timezone', 'N/A'),
            "Last Updated": convert_timestamp(system_metadata.get('last_updated', 0)),
            "Version": system_metadata.get('version'),
            "Format": "GBFS"  
        })

df = pd.DataFrame(metadata_list)

output_file = 'C:/Users/m-de-pastor/Desktop/Un peut tout/norvege.xlsx'
df.to_excel(output_file, index=False)

print(f"Les métadonnées GBFS ont été enregistrées dans le fichier {output_file}")
