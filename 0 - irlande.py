import requests
from bs4 import BeautifulSoup
import pandas as pd
from transformers import pipeline


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


def get_dataset_metadata(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve the page at {url}")

    soup = BeautifulSoup(response.content, "html.parser")

    metadata = {}

    # Titre
    title_tag = soup.find("h1")
    metadata['Titre'] = title_tag.text.strip() if title_tag else 'N/A'

    # Publié par
    published_by_tag = soup.find("div", class_="dataset-top-meta").find("h5")
    metadata['Publié par'] = published_by_tag.find("strong").text.strip() if published_by_tag else 'N/A'

    # Licence
    license_tag = soup.find("h5", property="dc:rights")
    if license_tag:
        license_link = license_tag.find("a")
        metadata['Licence'] = license_link.text.strip() if license_link else 'N/A'
    else:
        metadata['Licence'] = 'N/A'

    # Catégorie
    category_tag = soup.find("div", class_="dataset-top-meta").find_all("h5")
    category_text = next((h5.find("strong").text.strip() for h5 in category_tag if "Category:" in h5.text), 'N/A')
    metadata['Catégorie'] = category_text

    # Openness rating
    openness_tag = soup.find("div", class_="qa")
    if openness_tag:
        class_list = openness_tag['class']
        for class_name in class_list:
            if class_name.startswith("openness-"):
                stars = class_name.split("-")[-1]
                metadata['Openness rating'] = f"{stars} étoiles"
                break
        else:
            metadata['Openness rating'] = 'N/A'
    else:
        metadata['Openness rating'] = 'N/A'

    # Formats
    formats = []
    format_tags = soup.find_all("div", class_="dataset-resource-format")
    for format_tag in format_tags:
        format_name = format_tag.find("span", class_="format-name").text.strip()
        formats.append(format_name)
    metadata['Format'] = ', '.join(formats)

    info_table = soup.find("section", class_="additional-info").find("table")
    for row in info_table.find_all("tr"):
        th = row.find("th").text.strip()
        td = row.find("td").text.strip()
        if th == "Data Owner":
            metadata['Data Owner'] = td
        elif th == "Data Owner Email":
            metadata['Data Owner Email'] = td
        elif th == "Data Owner Telephone":
            metadata['Data Owner Telephone'] = td
        elif th == "Theme":
            metadata['Theme'] = td
        elif th == "Date updated":
            metadata['Date updated'] = td
        elif th == "Language":
            metadata['Language'] = td

    return metadata

norway_urls = url_ireland()
metadata_no=[]

for url in norway_urls:
    metadata_no.append(get_dataset_metadata(url))

df = pd.DataFrame(metadata_no)


"""
nlp_classifier = pipeline("zero-shot-classification")
categories = ["car", "bus", "train", "plane", "boat"]

def predict_mode(title):
        result = nlp_classifier(title, candidate_labels=categories)
        return result['labels'][0] if result['scores'][0] > 0.5 else 'unknown'

df['Mode de transport'] = df['Titre'].apply(predict_mode)


"""


df.to_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/ireland_test.xlsx', index=False)