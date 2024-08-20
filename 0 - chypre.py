import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_dataset_urls(url):
    response = requests.get(url)
    response.raise_for_status()  # Vérifie que la requête a réussi
    soup = BeautifulSoup(response.text, 'html.parser')
    dataset_items = soup.find_all('li', class_='dataset-item')
    dataset_urls = ['https://www.traffic4cyprus.org.cy' + item.find('a')['href'] for item in dataset_items]
    return dataset_urls

def get_dataset_metadata(dataset_url):
    response = requests.get(dataset_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    metadata = {}
    
    # Titre
    metadata['Titre'] = soup.find('h1').text.strip()
    
    # Description
    desc_tag = soup.find('section', class_='additional-info').find('p')
    metadata['Description'] = desc_tag.text.strip() if desc_tag else ''
    
    # Langue des métadonnées
    language_tag = soup.find('td', property='dct:language')
    metadata['Langue des métadonnées'] = language_tag.text.strip() if language_tag else ''
    
    # Mail publieur
    author_email_tag = soup.find('th', string='Author Email')
    if author_email_tag:
        author_email_tag = author_email_tag.find_next_sibling('td').find('a')
    metadata['Mail publieur'] = author_email_tag['href'].replace('mailto:', '') if author_email_tag else ''
    
    # Fréquence d'actualisation
    frequency_tag = soup.find('td', property='dct:accrualPeriodicity')
    metadata['Fréquence d\'actualisation'] = frequency_tag.text.strip() if frequency_tag else ''
    
    # Thème
    theme_tag = soup.find('td', property='dcat:theme')
    metadata['Thème'] = theme_tag.text.strip() if theme_tag else ''
    
    # Mode de transport
    transport_mode_tag = soup.find('td', property='mobilitydcatap:transportMode')
    metadata['Mode de transport'] = ', '.join([li.text for li in transport_mode_tag.find_all('li')]) if transport_mode_tag else ''
    
    # Couverture territoriale
    coverage_tag = soup.find('td', property='mobilitydcatap:networkCoverage')
    metadata['Couverture territoriale'] = ', '.join([li.text for li in coverage_tag.find_all('li')]) if coverage_tag else ''
    
    # Publié par
    author_tag = soup.find('th', string='Author')
    if author_tag:
        author_tag = author_tag.find_next_sibling('td')
    metadata['Publié par'] = author_tag.text.strip() if author_tag else ''
    
    # Propriétaire des données
    maintainer_tag = soup.find('th', string='Maintainer')
    if maintainer_tag:
        maintainer_tag = maintainer_tag.find_next_sibling('td')
    metadata['Propriétaire des données'] = maintainer_tag.text.strip() if maintainer_tag else ''
    
    # Licences
    license_tag = soup.find('th', string='License')
    if license_tag:
        license_tag = license_tag.find_next_sibling('td').find('a')
    metadata['Licence Combinée Simplifiée'] = license_tag.text.strip() if license_tag else ''
    
    # Tags
    tags_section = soup.find('section', class_='tags')
    if tags_section:
        tags = [tag.text.strip() for tag in tags_section.find_all('a', class_='tag')]
        metadata['Tags_chypre'] = ', '.join(tags)
    
    # Collecter les informations de chaque ressource
    resources = []
    resource_items = soup.find_all('li', class_='resource-item')
    for resource_item in resource_items:
        resource = metadata.copy()  # Copie des métadonnées principales
        resource['url vers le jeu de données'] = 'https://www.traffic4cyprus.org.cy' + resource_item.find('a', class_='heading')['href']
        resource['Titre de la ressource'] = resource_item.find('a', class_='heading').text.strip()
        resource['Format'] = resource_item.find('span', class_='format-label').text.strip()
        
        more_info_url = resource['url vers le jeu de données']
        
        # Extraire les métadonnées additionnelles de la page "More information"
        resource.update(get_additional_resource_info(more_info_url))
        
        resources.append(resource)
    
    return resources

def get_additional_resource_info(more_info_url):
    response = requests.get(more_info_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    additional_metadata = {}
    
    # Data last updated
    last_updated_tag = soup.find('th', string='Data last updated')
    if last_updated_tag:
        last_updated_tag = last_updated_tag.find_next_sibling('td')
    additional_metadata['Dernière mise à jour de la ressource'] = last_updated_tag.text.strip() if last_updated_tag else ''
    
    # Metadata last updated
    metadata_updated_tag = soup.find('th', string='Metadata last updated')
    if metadata_updated_tag:
        metadata_updated_tag = metadata_updated_tag.find_next_sibling('td')
    additional_metadata['Date de création'] = metadata_updated_tag.text.strip() if metadata_updated_tag else ''
    
    # License
    license_tag = soup.find('th', string='License')
    if license_tag:
        license_tag = license_tag.find_next_sibling('td').find('a')
    additional_metadata['Licence Combinée Simplifiée'] = license_tag.text.strip() if license_tag else ''
    
    # Qualité du jeu de données
    quality_tag = soup.find('th', string='Conditions for access and usage')
    if quality_tag:
        quality_tag = quality_tag.find_next_sibling('td')
    additional_metadata['Qualité du jeu de données'] = quality_tag.text.strip() if quality_tag else ''
    
    # Valide depuis
    created_tag = soup.find('th', string='Created')
    if created_tag:
        created_tag = created_tag.find_next_sibling('td')
    additional_metadata['Valide depuis'] = created_tag.text.strip() if created_tag else ''
    
    return additional_metadata

# URL de la page contenant les datasets
url = 'https://www.traffic4cyprus.org.cy/dataset/'

# Récupérer les URLs des datasets
dataset_urls = get_dataset_urls(url)

# Collecter les métadonnées de chaque dataset
all_metadata = []
for dataset_url in dataset_urls:
    dataset_metadata = get_dataset_metadata(dataset_url)
    all_metadata.extend(dataset_metadata)

# Créer un DataFrame avec toutes les métadonnées
df = pd.DataFrame(all_metadata)
print(df)

df.to_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/chypre.xlsx', index=False)




