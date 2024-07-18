import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from langdetect import detect, LangDetectException


URL_BASE={
'belgium' : 'https://www.transportdata.be/fr/dataset/' ,       #on se permet de considérer que ces liens ne changeront pas
'spain' : 'https://nap.transportes.gob.es/Files/List' ,
'luxembourg' : 'https://data.public.lu/fr/pages/topics/mobility/' ,
'italy' : 'https://nap-1926.it/nap/mmtis/public/_next/data/wQL-zdR43tmSYD_zIPqtY/it/catalog/Dataset.json?query=&offset=0&filters=&maxRows=50&orderBy=DEFAULT&type=Dataset' #pour l'italie, c'est un json
}

def extract_url_dataset(url, country='belgium'):
    all_dataset_urls = []
    
    if country == 'belgium':
        while url:
            response_base = requests.get(url)
            if response_base.status_code == 200:
                soup = BeautifulSoup(response_base.text, 'html.parser')
                dataset_links = soup.select('h3.dataset-heading a')
                all_dataset_urls.extend(['https://www.transportdata.be' + link['href'] for link in dataset_links])
                
                pagination = soup.find('ul', class_='pagination')
                if pagination:
                    next_page_link = pagination.find('a', string='»')
                    if next_page_link:
                        url = 'https://www.transportdata.be' + next_page_link['href']
                    else:
                        url = None
                else:
                    url = None
            else:
                print(f"Erreur : Impossible de récupérer la page. Statut : {response_base.status_code}")
                url = None
    
    elif country == 'spain':
        page = 1
        while True:
            current_url = f"{url}?showFilterTT=False&showFilterR=False&showfilterAU=False&showFilterTF=False&search=&orderby=Recientes&page={page}"
            response = requests.get(current_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                dataset_items = soup.select('h3.card-title-hidden a, h3.card-title.hidden-title a')
                if not dataset_items:
                    break
                all_dataset_urls.extend([urljoin(current_url, item['href']) for item in dataset_items])
                page += 1
            else:
                print(f"Erreur : Impossible de récupérer la page {page}. Statut : {response.status_code}")
                break
    
    elif country == 'luxembourg':
        page_number = 1
        url_site = 'https://data.public.lu'
        url_pagination = f'{url}?datasets_page={page_number}'
        while True:
            
            response = requests.get(url_pagination)
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                dataset_articles = soup.find_all('article', class_='fr-pt-5v fr-pb-6v fr-px-1w border-bottom border-default-grey fr-enlarge-link')

                if not dataset_articles:
                    break

                for article in dataset_articles:
                    dataset_link = article.find('a', class_='text-grey-500')['href']
                    dataset_url = urljoin(url_site, dataset_link)
                    all_dataset_urls.append(dataset_url)

                page_number += 1
                url_pagination = f'{url}?datasets_page={page_number}'

            else:
                break
        return all_dataset_urls
    
    elif country == 'Italy':
        pass
        #pas besoin, à voir si je rajoute une colonne url...

    else:
        print("Pays non pris en charge pour le moment.")
    
    return list(set(all_dataset_urls))

def fetch_html_content(url):
    # pour récupérer le HTML à partir de l'URL
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to retrieve HTML content from {url}. Status code: {response.status_code}")
        return None



urls_belgium = extract_url_dataset(URL_BASE['belgium'], 'belgium')
urls_spain = extract_url_dataset(URL_BASE['spain'], 'spain')
urls_luxembourg = extract_url_dataset(URL_BASE['luxembourg'], 'luxembourg')

all_all_dataset_urls = urls_belgium + urls_spain + urls_luxembourg      #en soi all__all_dataset_urls ne va pas vraiment nous intéresser, il vaut mieux garder urls_belgium...

print(len(all_all_dataset_urls), len(urls_belgium), len(urls_spain), len(urls_luxembourg))
print(all_all_dataset_urls)





def extract_metadata_values(soup): #espagne uniquement pour le moment 
    metadata = {}

    # Trouver toutes les div contenant les métadonnées
    metadata_divs = soup.find_all('div', class_='divMetadatosCard')

    for div in metadata_divs:
        # Les métadonnées sont classées en différentes catégories
        category_title_element = div.find('span', class_='font-weight-bold')
        if category_title_element:
            category_title = category_title_element.text.strip()

            # Trouver toutes les lignes de métadonnées dans cette catégorie
            rows = div.find_all('tr')

            for row in rows:
                # Extraire la clé (nom de la métadonnée) et la valeur
                columns = row.find_all('td')   #on est sur une structure <tr> <td> cle de la metadonnee </td> <td> valeur de la metadonnee </td> </tr>
                if len(columns) == 2:
                    key = columns[0].text.strip()
                    value = columns[1].text.strip()

                    # Ajouter la métadonnée uniquement si la clé et la valeur ne sont pas vides
                    if key and value:
                        metadata[key] = value

    return metadata


def add_suffix_to_keys(metadata_dict, suffix): #pour ajouter le nom du pays à la fin des colonnes pour s'y retrouver
    new_metadata_dict = {}
    for key, value in metadata_dict.items():
        new_key = f"{key}_{suffix}"
        new_metadata_dict[new_key] = value
    return new_metadata_dict



def extract_text_or_link(tag):
    if tag:
        link = tag.find('a')
        if link:
            return link['href']
        return tag.get_text(strip=True)
    return 'N/A'


def detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return 'Unknown'
    


def get_dataset_metadata_be(dataset_url):
    dataset_id = dataset_url.split('/')[-1]
    api_url = f'https://www.transportdata.be/api/3/action/package_show?id={dataset_id}'
    
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            result = data['result']
            response_page = requests.get(dataset_url)
            if response_page.status_code == 200:
                soup = BeautifulSoup(response_page.text, 'html.parser')

                def extract_metadata_value(label):
                    #Extract metadata value pour un label donné. Attention, il y a des cas particuliers pour lesquels le html est un peu différent, par exemple parfois il n'y a pas 'dataset-details'.
                    if label == 'ID':
                        th_tag = soup.find('th', string='ID')
                        if th_tag:
                            td_tag = th_tag.find_next_sibling('td')
                            if td_tag:
                                return td_tag.get_text(strip=True)
                    else:
                        th_tags = soup.find_all('th', class_='dataset-label')
                        for th_tag in th_tags:
                            if th_tag.get_text(strip=True) == label:
                                td_tag = th_tag.find_next_sibling('td', class_='dataset-details')
                                if td_tag:
                                    return extract_text_or_link(td_tag)
                    return 'N/A'

                

                
                metadata_languages_tag = soup.find('td', {'property': 'dct:language'})
                if metadata_languages_tag:
                    languages = [li.get_text(strip=True) for li in metadata_languages_tag.find_all('li')]
                    metadata_languages_str = ', '.join(languages) if languages else metadata_languages_tag.get_text(strip=True)
                else:
                    metadata_languages_str = 'N/A'

                format_tag = soup.find('span', class_='format-label')
                format_value = format_tag.get_text(strip=True) if format_tag else 'N/A'

                mode_transport_tags = soup.select('ul.tag-list a.tag')
                mode_transport_values = [tag.get_text(strip=True) for tag in mode_transport_tags]
                mode_transport_str = ', '.join(mode_transport_values) if mode_transport_values else 'N/A'
                
                metadata_be = {
                    'Nom': result.get('title', 'N/A'),
                    'ID': extract_metadata_value('ID'),
                    'Date des métadonnées': extract_metadata_value('Metadata date'),
                    'Langue des métadonnées': metadata_languages_str,
                    'Type de NAP': extract_metadata_value('NAP type'),
                    'Type du jeu de données': extract_metadata_value('Dataset Type'),
                    'Type de ressource': extract_metadata_value('Resource type'),
                    'Nom [point de contact]': extract_metadata_value('Name [contact point]'),
                    'Nom de l\'organisation [éditeur]': extract_metadata_value('Organisation name [publisher]'),
                    'Nom [éditeur]': extract_metadata_value('Name [publisher]'),
                    'Adresse [éditeur]': extract_metadata_value('Address [publisher]'),
                    'E-mail [éditeur]': extract_metadata_value('E-mail [publisher]'),
                    'Site web [éditeur]': extract_metadata_value('Website [publisher]'),
                    'Numéro de téléphone [éditeur]': extract_metadata_value('Telephone number [publisher]'),
                    'Date de début de publication': extract_metadata_value('Start date of publication'),
                    'Date de fin de publication': extract_metadata_value('End date of publication'),
                    'Pays couverts par la publication': extract_metadata_value('Countries covered by publication'),
                    'Zone couverte par la publication': extract_metadata_value('Area covered by publication'),
                    'Portée du jeu de données': extract_metadata_value('Dataset extent'),
                    'Contrat ou licence': extract_metadata_value('Contract or license'),
                    'Type de licence': extract_metadata_value('License type'),
                    'Fréquence de mise à jour': extract_metadata_value('Update frequency'),
                    'Evaluation de la qualité': extract_metadata_value('Quality assessment'),
                    'Thème du jeu de données': extract_metadata_value('Dataset theme'),
                    'Format' : format_value,
                    'Mode de transport': mode_transport_str
                }
                #metadata_be = add_suffix_to_keys(metadata_be, 'belgium')
                return metadata_be
            else:
                print(f"Erreur lors de la requête de la page HTML: {response_page.status_code} pour {dataset_url}.")
        else:
            print(f"Erreur: Réponse API sans succès pour {dataset_id}.")
    else:
        print(f"Erreur lors de la requête API: {response.status_code} pour {dataset_id}.")
    return None

def get_dataset_metadata_es(dataset_url):
    # Récupérer le contenu HTML de l'URL
    html_content = fetch_html_content(dataset_url)
    if html_content:
        # Parser le contenu HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extraire les métadonnées
        metadata = extract_metadata_values(soup)
        #metadata = add_suffix_to_keys(metadata, '_spain')
        #metadata['Format'] = metadata.pop('Modelo')
        return metadata
    else:
        print(f"Failed to retrieve HTML content from {dataset_url}.")
        return None

def get_dataset_metadata_lu(url):
    dataset_id = url.rstrip('/').split('/')[-1] #id à partir de l'url du dataset
    
    api_url = f'https://data.public.lu/api/1/datasets/{dataset_id}/' #url api
    
    response = requests.get(api_url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve dataset information. Status code: {response.status_code}")
    
    metadata = response.json()
    #print(metadata.keys())
    #print(metadata.values())
    
    #on prend tout 
    metadata_dict = {
        'Titre': metadata.get('title', 'N/A'),
        'Licence': metadata.get('license', 'N/A'),
        'ID': metadata.get('id', 'N/A'),
        'Fréquence': metadata.get('frequency', 'N/A'),
        'Date de création': metadata.get('created_at', 'N/A'),
        'Dernière mise à jour de ressource': metadata.get('last_modified', 'N/A'),
        'Granularité de la couverture territoriale': 'N/A',    #valeur par défaut 
        'URL de l\'organisation': 'N/A',
        'Tags': ', '.join(metadata.get('tags', [])),
        'Acronyme': metadata.get('acronym', 'N/A'),
        'Archivé': metadata.get('archived', 'N/A'),
        'Badges': ', '.join(badge['kind'] for badge in metadata.get('badges', [])),
        'Description': metadata.get('description', 'N/A'),
        'Extras': metadata.get('extras', 'N/A'),
        'Date de fréquence': metadata.get('frequency_date', 'N/A'),
        'Date de dernière mise à jour': metadata.get('last_update', 'N/A'),
        'Propriétaire': metadata.get('owner', 'N/A'),
        'Page': metadata.get('page', 'N/A'),
        'Privé': metadata.get('private', 'N/A'),
        'Qualité': metadata.get('quality', 'N/A'),
        'Ressources': ', '.join(resource['title'] for resource in metadata.get('resources', [])),
        'Slug': metadata.get('slug', 'N/A'),
        'Couverture temporelle': metadata.get('temporal_coverage', 'N/A'),
        'URI': metadata.get('uri', 'N/A')
    }

    response_page = requests.get(url)
    if response_page.status_code == 200:
        soup = BeautifulSoup(response_page.text, 'html.parser')
        script_tag = soup.find('script', {'id': 'json_ld', 'type': 'application/ld+json'})
        
        if script_tag:
            json_data = json.loads(script_tag.string)
            distributions = json_data.get('distribution', [])
            if distributions:
                formats = [dist.get('encodingFormat', 'N/A') for dist in distributions]
                format_value = ', '.join(formats)
            else:
                format_value = 'N/A'
        else:
            format_value = 'N/A'
    else:
        format_value = 'N/A'

    metadata_dict['Format'] = format_value

    if metadata.get('spatial'):
        metadata_dict['Granularité de la couverture territoriale'] = metadata['spatial'].get('granularity', 'N/A')
    
    if metadata.get('organization'):
        metadata_dict['URL de l\'organisation'] = metadata['organization'].get('page', 'N/A')
    
    metadata_title = metadata.get('title', '')
    if metadata_title and metadata_title != 'N/A':
        detected_language = detect_language(metadata_title)
        metadata_dict['Langue des métadonnées'] = detected_language.capitalize()
    else:
        metadata_dict['Langue des métadonnées'] = 'N/A'

    #metadata = add_suffix_to_keys(metadata, '_luxembourg')
    return metadata_dict

def get_dataset_metadata_it(json_url):    #attention cette fonction renvoie toutes les métadonnées de tous les datasets alors que be es et lu c'est que les métadonnées de l'url passé en entrée
    response = requests.get(json_url)
    json_data = response.text
    data = json.loads(json_data)
    
    datasets_metadata = []
    
    for dataset in data['pageProps']['searchResults']:
        metadata = {}
        # métadonnées qui sont pas dans Attributes
        metadata['name'] = dataset.get('name')
        metadata['creationDate'] = dataset.get('creationDate')
        metadata['lastModificationDate'] = dataset.get('lastModificationDate')
        
        # métadonnées qui sont dans les attributs (la plupart des métadonnées le sont)
        for attribute in dataset.get('attributes', []):
            title_en = attribute['title'].get('en')
            value = attribute['value']
            if isinstance(value, dict) and 'translations' in value:
                value = value['translations'].get('en', value['value'])
            elif isinstance(value, list) and title_en == "NeTEx category":
                value = ', '.join(item['translations']['en'] for item in value)
            metadata[title_en] = value
        
        # juste pour la description
        if 'Description' in metadata and isinstance(metadata['Description'], dict):
            metadata['Description'] = metadata['Description'].get('en', metadata['Description'])
        
        # Renommer 'Tags' en 'Tags_italy' pour pas confondre avec les autres pays
        if 'Tags' in metadata:
            metadata['Tags_italy'] = metadata.pop('Tags')
        
        network_description = metadata.get('Network coverage description', {})
        metadata['Network coverage description'] = network_description.get('en', network_description)

        #metadata['Mode de transport'] = 'Train, Bus'
        
        datasets_metadata.append(metadata)
    
    #datasets_metadata = add_suffix_to_keys(datasets_metadata, '_italy')
    return datasets_metadata





country_metadata_extractors = {
    'spain': {
        'urls': urls_spain,
        'metadata_function': get_dataset_metadata_es
    },
    'belgium': {
        'urls': urls_belgium,
        'metadata_function': get_dataset_metadata_be
    },
    'luxembourg': {
        'urls': urls_luxembourg,
        'metadata_function' : get_dataset_metadata_lu
    }      #pas d'italie car il y a le json
}

metadata_list = []

for country, info in country_metadata_extractors.items():
    for url in info['urls']:
        metadata = info['metadata_function'](url)
        if metadata:
            metadata_list.append(metadata)

metadata_list += get_dataset_metadata_it(URL_BASE['italy'])

df = pd.DataFrame(metadata_list)

df['Format'] = df['Format'].fillna('') + df['Data format'].fillna('')
df.drop(columns=['Data format'], inplace=True)                               #pour l'italie

def clean_format(value):
    formats = value.split(', ')
    
    formats = list(set(formats))
    
    # Enlever les 'N/A' de la liste sauf si c'est la seule valeur
    if 'N/A' in formats and len(formats) > 1:
        formats.remove('N/A')
    
    return ', '.join(formats) if formats != ['N/A'] else 'N/A'

df['Format'] = df['Format'].apply(clean_format)
df['Format'] = df['Format'].str.upper()

df['Langue des métadonnées'] = df['Langue des métadonnées'].fillna('') + df['Languages of the dataset'].fillna('') + df['Lenguaje del conjunto de datos'].fillna('')
#df.drop(columns=['Data format'], inplace=True)       
#df.drop(columns=['Languages of the dataset'], inplace=True)       
#df.drop(columns=['Lenguaje del conjunto de datos'], inplace=True)       


df['Fréquence de mise à jour'] = df['Frecuencia de actualización'].combine_first(df['Fréquence de mise à jour']).combine_first(df['Update frequency'])
df = df.drop(columns=['Frecuencia de actualización', 'Update frequency'])

#Langues à remplacer
data_langues = {
    'Langue des métadonnées': ['spa', 'Fr', 'En', 'ca', 'De']
}

df['Langue des métadonnées'] = df['Langue des métadonnées'].replace({
    'spa': 'Spanish',
    'Fr': 'French',
    'En': 'English'
})

df['Langue des métadonnées'] = df['Langue des métadonnées'].apply(lambda x: 'Unknown' if len(x) == 2 and x not in ['Fr', 'En'] else x)



metadata_be_es = 'C:/Users/m-de-pastor/Desktop/Un peut tout/metadata_be_es_lu_it.xlsx'
df.to_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/metadata_be_es_lu_it.xlsx', index=False)

print(df)

