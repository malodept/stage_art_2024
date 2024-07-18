import requests
from bs4 import BeautifulSoup
import json

URL_BASE = {
    'belgium': 'https://www.transportdata.be/fr/dataset/',
    'spain': 'https://nap.transportes.gob.es/Files/List',
    'luxembourg': 'https://data.public.lu/fr/pages/topics/mobility/',
    'italy': 'https://nap-1926.it/nap/mmtis/public/_next/data/wQL-zdR43tmSYD_zIPqtY/it/catalog/Dataset.json?query=&offset=0&filters=&maxRows=50&orderBy=DEFAULT&type=Dataset'
}



def url_ireland():
    base_url = "https://data.gov.ie/dataset/?theme=Transport&api=true&page="
    urls = []

    for page in range(1, 20):
        response = requests.get(base_url + str(page))
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            dataset_items = soup.find_all("li", class_="dataset-item")
            
            for item in dataset_items:
                a_tag = item.find("a", href=True)
                if a_tag:
                    dataset_url = "https://data.gov.ie" + a_tag['href']
                    urls.append(dataset_url)
        else:
            print(f"Failed to retrieve page {page}")

    return urls

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
                all_dataset_urls.extend([requests.compat.urljoin(current_url, item['href']) for item in dataset_items])
                page += 1
            else:
                print(f"Erreur : Impossible de récupérer la page {page}. Statut : {response.status_code}")
                break

    else:
        print("Pays non pris en charge pour le moment.")
    
    return list(set(all_dataset_urls))

def save_urls_to_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file)

def load_urls_from_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def get_all_urls():
    url_data = {}
    
    # Irlande
    irish_urls = url_ireland()
    url_data['Irlande'] = irish_urls

    # Belgique
    belgium_urls = extract_url_dataset(URL_BASE['belgium'], country='belgium')
    url_data['Belgique'] = belgium_urls

    # Espagne
    spain_urls = extract_url_dataset(URL_BASE['spain'], country='spain')
    url_data['Espagne'] = spain_urls

    # Sauvegarde
    save_urls_to_json('urls_data.json', url_data)
    
    return url_data

# Exécuter la fonction et enregistrer les résultats dans un fichier JSON
url_data = get_all_urls()
with open('urls_data.json', 'w') as f:
    json.dump(url_data, f)
