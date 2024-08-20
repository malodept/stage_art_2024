import requests
import pandas as pd
from bs4 import BeautifulSoup


# Your API token
api_token = 'eyJvcmciOiI2NDA2NTFhNTIyZmEwNTAwMDEyOWJiZTEiLCJpZCI6ImYyYjQ3OWZhZjdjYTQ1OGFiYzA5Y2Y5YTVjMDdiZWQ1IiwiaCI6Im11cm11cjEyOCJ9'

# API URL
url = 'https://api.opentransportdata.swiss/ckan-api/package_list'

# Set up the headers with the authorization token
headers = {
    'Authorization': api_token
}

# Make the request
response = requests.get(url, headers=headers)

# Check the response
if response.status_code == 200:
    # Success
    data = response.json()
else:
    # Handle errors
    print(f"Error: {response.status_code} - {response.text}")

all_dataframes = []
for suffixe in data['result']:
    url_dataset=f'https://api.opentransportdata.swiss/ckan-api/package_show?id={suffixe}'

    # Make the request
    response_dataset = requests.get(url_dataset, headers=headers)

    # Check the response
    if response.status_code == 200:
        # Success
        data_dataset = response_dataset.json()
        df = pd.json_normalize(data_dataset["result"])
        all_dataframes.append(df)
        
    else:
        # Handle errors
        print(f"Error: {response.status_code} - {response.text}")
    

final_df = pd.concat(all_dataframes, ignore_index=True)

final_df = final_df.drop(columns=["author_email", "license_id", "license_title", "tags", "relationships_as_subject", "relationships_as_object", "organization.image_url", "force_all", "date_pattern", "bucket", "infoplus.dataset", "infoplus.year", "infoplus.files.BAHNHOF", "infoplus.files.BFKOORD_GEO", "resource_regex", "timetable_regex", "ist_file", "filter_regex", "status.last_job.object_error_summary", "status.last_job.stats.deleted", "status.last_job.stats.errored", "status.last_job.stats.not modified", "status.last_job.stats.updated", "status.last_job.stats.added"])



def get_format_from_html(dataset_name):     #dans le cas où le format n'est ni gtfs ni netex
    base_url = 'https://opentransportdata.swiss/fr/dataset/'
    url = f'{base_url}{dataset_name}'       
    
    response = requests.get(url)
    if response.status_code != 200:
        return ''  

    soup = BeautifulSoup(response.content, 'html.parser')
    
    resource_items = soup.find_all('li', class_='resource-item')
    for item in resource_items:
        format_label = item.find('span', class_='format-label')
        if format_label:
            return format_label.get('data-format', '').upper()
    
    return '' 
# Fonction pour obtenir le format à partir des mots-clés ou du HTML
def get_format(keywords, dataset_name):
    if isinstance(keywords, list):
        for keyword in keywords:
            if 'gtfs' in keyword.lower():
                return 'GTFS'
            elif 'netex' in keyword.lower():
                return 'NETEX'               #déjà on regarde si le format est donnée dans les mots-clés (gtfs ou netex) et sinon, on va cherche dans le html
    return get_format_from_html(dataset_name)

# Parcourir chaque ligne de final_df et mettre à jour la colonne 'Format'
formats = []
for index, row in final_df.iterrows():
    keywords = row['keywords.en']
    dataset_name = row['name']
    format = get_format(keywords, dataset_name)
    formats.append(format)

final_df['Format'] = formats



columns_to_drop = final_df.filter(regex='(it|de|fr)$').columns
final_df = final_df.drop(columns=columns_to_drop)


final_df.to_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/suisse.xlsx', index=False)


print(list(final_df.columns))
