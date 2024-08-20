"""
Organisation du code :

1 : Pour chaque pays on écrit un programme qui permet d'enregistrer un excel en prenant beaucoup de métadonnées, au moins les plus importantes si elles existent
(thème, url, date création, dernière màj, date début validité, date fin validité, format, mode de transport, owner, publié par, coverage, score de qualité, description, licence, nb_reutilisations, langue des métadonnées, mail)
On considère que les colonnes seront traitées (fusionnées, renommées...) plus tard dans gestion_colonnes.py.

Si ce pays a besoin d'ia (par exemple le luxembourg pour détecter le mode de transport), on fait un fichier en plus spécialement pour cette colonne de ce pays car le temps d'éxécution peut être long (2h pour le luxembourg)

2 : Ensuite, on concatène les fichiers des pays avec concat.py, qui enregistre fichiers_concatenes.xlsx.

3 : On gère le traitement des colonnes dans gestion_colonnes.py. Cela permet d'uniformiser les données (fréquences d'actualisation par exemple), supprimer des colonnes inutiles, fusionner, renommer...
On fait une fonction par colonne et à l'intérieur on gère cette colonne pour tous les pays concernés. 
On obtient fichiers_concatenes_colonnes_gerees.xlsx.

4 : On s'occupe du tableau qui permet de suivre avec plus de recul la présence ou non d'une certaine colonne pour un certain pays, dans le fichier suppression_lignes_de_pays_metadonne.py
"""


import pandas as pd
import numpy as np
import json

data_frame=pd.read_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/fichiers_concatenes.xlsx')


excel_files = ['C:/Users/m-de-pastor/Desktop/Un peut tout/ireland_transfo.xlsx', 
               'C:/Users/m-de-pastor/Desktop/Un peut tout/luxembourg_transfo_3_gpt4all.xlsx', 
               'C:/Users/m-de-pastor/Desktop/Un peut tout/espagne_transfo.xlsx', 
               'C:/Users/m-de-pastor/Desktop/Un peut tout/italie_transfo.xlsx', 
               'C:/Users/m-de-pastor/Desktop/Un peut tout/belgique_transfo.xlsx',
               'C:/Users/m-de-pastor/Desktop/Un peut tout/chypre.xlsx',
               ]
"""
df_irlande = pd.read('C:/Users/m-de-pastor/Desktop/Un peut tout/ireland_transfo.xlsx')
df_luxembourg = pd.read('C:/Users/m-de-pastor/Desktop/Un peut tout/luxembourg_transfo_3_gpt4all.xlsx')
df_espagne = pd.read('C:/Users/m-de-pastor/Desktop/Un peut tout/espagne_transfo.xlsx')
df_italie = pd.read('C:/Users/m-de-pastor/Desktop/Un peut tout/italie_transfo.xlsx')
df_belgique = pd.read('C:/Users/m-de-pastor/Desktop/Un peut tout/belgique_transfo.xlsx')
df_chypre = pd.read('C:/Users/m-de-pastor/Desktop/Un peut tout/chypre.xlsx')

"""
def gestion_url(df):
    # Vérifier si les colonnes 'Page' et 'url vers le jeu de données' existent dans le DataFrame
    if 'Page' in df.columns and 'url vers le jeu de données' in df.columns:       #Ici on s'est occupé du luxembourg et de chypre
        # Fusionner les colonnes en une seule colonne 'URL'
        df['URL'] = df['Page'].combine_first(df['url vers le jeu de données'])
        # Supprimer les colonnes d'origine
        df.drop(columns=['Page', 'url vers le jeu de données'], inplace=True)
    
    # Charger les URLs depuis le fichier JSON
    with open('urls_data.json', 'r') as file:        #le fichier json a été enregistré dans extraction_urls.py
        url_data = json.load(file)
    
    # Itérer sur chaque pays et ses URLs correspondants
    for country, urls in url_data.items():
        # Vérifier si le pays existe dans le DataFrame
        if 'Pays' in df.columns and country in df['Pays'].unique():
            # Récupérer les indices des lignes correspondant au pays
            indices = df.index[df['Pays'] == country].tolist()
            for idx in indices:
                df.loc[idx, 'URL'] = urls[idx % len(urls)]  
        else:
            print(f"Aucune ligne pour le pays {country} trouvée dans le DataFrame.")

   
    italy_object_ids = [
        93457, 93484, 61753, 101931, 101958, 228171, 222859, 28205, 2286, 8812,
        136123, 178320, 139278, 66, 83, 74238, 227230, 51161, 51188, 2412,
        5521, 228484, 9598, 52759, 51219, 176683, 241548, 241590
    ]
    
    italy_base_url = "https://nap-1926.it/nap/mmtis/public/catalog/Dataset/"
    italy_urls = [f"{italy_base_url}{object_id}" for object_id in italy_object_ids]
    
    if 'Pays' in df.columns and 'Italie' in df['Pays'].unique():
        italy_indices = df.index[df['Pays'] == 'Italie'].tolist()
        for idx, italy_idx in enumerate(italy_indices):
            df.loc[italy_idx, 'URL'] = italy_urls[idx % len(italy_urls)]  

    return df

def formats(df):
    def remove_duplicates(cell):
        if isinstance(cell, str):
            items = cell.split(', ')
            unique_items = set(items)
            return ', '.join(sorted(unique_items))
        return cell

    # Nettoyer la colonne 'Format'
    df['Format'] = df['Format'].apply(remove_duplicates)
    
    # Définir les pays à traiter
    countries_to_process = ['Irlande', 'Luxembourg']
    
    for country in countries_to_process:
        # Filtrer le DataFrame pour le pays spécifié
        df_country = df[df['Pays'] == country].copy()
        
        # Calculer les pourcentages des formats
        total_count = df_country.shape[0]
        format_counts = df_country['Format'].value_counts()
        format_percentages = (format_counts / total_count) * 100
        
        # Remplacer les formats inférieurs à 3% par 'OTHER'
        df.loc[df['Pays'] == country, 'Format'] = df_country['Format'].apply(lambda x: 'OTHER' if x and format_percentages.get(x, 0) < 3 else x)
    
    df['Format'] = df['Format'].str.split(', ')
    df_exploded = df.explode('Format').reset_index(drop=True)
    return df_exploded
    
def split_langues(df):
    df['Langue des métadonnées'] = df['Langue des métadonnées'].str.split(', ')
    df_exploded = df.explode('Langue des métadonnées').reset_index(drop=True)
    return df_exploded
    #df_exploded.to_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/fichiers_concatenes.xlsx', index=False)

def liste_des_freq_d_actualisation(df):

    df["Fréquence d'actualisation"] = df[['Frecuencia de actualización', 'Fréquence de mise à jour', 'Fréquence', 'Update frequency']].bfill(axis=1).iloc[:, 0]

    frequency_mapping = {
    'Less frequent than yearly': 'Other/On occurence',
    'On occurence': 'Other/On occurence',
    'Up to 12h': 'Hourly',
    'Up to 15min': 'More Frequent',
    'Up to 5min': 'More Frequent',
    'Up to 1h': 'Hourly',
    'Up to 1min': 'More Frequent',
    'Up to 24h': 'Daily',
    'Up to Monthly': 'Monthly',
    'Up to Weekly': 'Weekly',
    'Up to Weekly;': 'Weekly',
    'Up to every 3 month': 'Monthly',
    'Up to every 3month': 'Monthly',
    'Up to every 6 month': 'Weekly',
    'Up to every 6month': 'Weekly',
    'Up to yearly': 'Yearly',
    'annual': 'Yearly',
    'continuous': 'More Frequent',
    'daily': 'Daily',
    'hourly': 'Hourly',
    'irregular': 'Other/On occurence',
    'monthly': 'Monthly',
    'punctual': 'More Frequent',
    'quarterly': 'Monthly',
    'quinquennial': 'Other/On occurence',
    'triennial': 'Monthly',
    'unknown': 'Other/On occurence',
    'weekly': 'Weekly',
    #ajout de chypre
    'Up to 1 min' : 'More Frequent',
    'Up to every 3 month' : 'Monthly',
    'Up to 5min' : 'More Frequent',
    #ajout de suisse
    'freq:daily' : 'Daily',
    'freq:continuous' : 'More Frequent',
    'freq:irregular' : 'Other/On occurence',
    'freq:yearly' : 'Yearly'
    }


    df["Fréquence d'actualisation"] = df["Fréquence d'actualisation"].apply(lambda x: frequency_mapping.get(x, np.nan))

    return df
    #df.to_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/fichiers_concatenes.xlsx', index=False)

def gestion_licence_2(df):
    df['Licence Combinée'] = df.apply(lambda row: row['Contrat ou licence'] if row['Pays'] == 'Belgique' else (row['Type de licence'] if row['Pays'] == 'Belgique' else row['Licence']), axis=1)

    df['Licence Combinée'] = df.apply(lambda row: 'Licence and Free of charge' if row['Pays'] == 'Espagne' else row['Licence Combinée'], axis=1)

    licence_mapping = {
    'Belgique': {
        'Contract and Fee': 'Contract and Fee',
        'Contract and Free of charge': 'Licence and Free of charge',
        'Licence and Fee': 'Licence and Fee',
        'Licence and Free of charge': 'Licence and Free of charge',
        'No license – No contract': 'No license',
        'Not relevant': 'Other/Unknown',
        'Not specified': 'Other/Unknown',
        'cc-by': 'Creative Commons',
        'cc-by-sa': 'Creative Commons',
        'cc-nc': 'Creative Commons',
        'cc-zero': 'Creative Commons Zero',
        'notspecified': 'Other/Unknown',
        'odc-by': 'Open Data Commons',
        'other-closed': 'Other/Unknown',
        'other-nc': 'Other/Unknown',
        'other-open': 'Other Open',
        'other-pd': 'Other/Unknown',
        'uk-ogl': 'Other/Unknown'
    },
    'Espagne': {
        'Licence and Free of charge': 'Licence and Free of charge'
    },
    'Luxembourg': {
        'Creative Commons Attribution 4.0': 'Creative Commons',
        'cc-by': 'Creative Commons',
        'cc-by-sa': 'Creative Commons',
        'cc-zero': 'Creative Commons Zero',
        'notspecified': 'Other/Unknown',
        'odc-by': 'Open Data Commons',
        'other-open': 'Other Open'
    },
    'Irlande': {
        'Creative Commons Attribution 4.0': 'Creative Commons'
    },
    'Italie': {
        np.nan: 'Other/Unknown'
    },
    'Chypre': {
        'Creative Commons Attribution 4.0': 'Creative Commons'
    }
}

    def map_licence(row):
        country = row['Pays']
        licence = row['Licence Combinée']
        if country in licence_mapping and licence in licence_mapping[country]:
            return licence_mapping[country][licence]
        return 'Other/Unknown'

    df['Licence Combinée Simplifiée'] = df.apply(map_licence, axis=1)

    print(df[['Pays', 'Licence Combinée Simplifiée']].head())

    count_df = df.groupby(['Licence Combinée Simplifiée', 'Pays']).size().reset_index(name='Count')
    licences = {row["Licence Combinée Simplifiée"]: (row['Pays'], row['Count']) for _, row in count_df.iterrows()}

    print(licences)
    return df

    #df.to_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/fichiers_concatenes.xlsx', index=False)

def gestion_publie_par(df): 
    df["Publié par"] = df["Publié par"].combine_first(df["Publisher"])
    df["Publié par"] = df["Publié par"].combine_first(df["Nom de l'organisation [éditeur]"])
    df["Publié par"] = df["Publié par"].combine_first(df["Nombre de la organización del Responsable de la publicación"])


    df = df.drop(columns=["Publisher", "Nom de l'organisation [éditeur]", "Nombre de la organización del Responsable de la publicación"])

    return df

    #df.to_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/fichiers_concatenes.xlsx', index=False)

def gestion_titre(df):
    df['Titre'] = df['Titre'].combine_first(df['Nombre del conjunto de datos'])
    df['Titre'] = df['Titre'].combine_first(df['Nom'])
    df['Titre'] = df['Titre'].combine_first(df['name'])


    df = df.drop(columns=["Nombre del conjunto de datos", "Nom", "name"])


    

    return df 

    #df.to_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/fichiers_concatenes.xlsx', index=False)

def gestion_langue(df):
    df.loc[df['Pays'] == 'Irlande', 'Langue des métadonnées'] = df.loc[df['Pays'] == 'Irlande', 'Language']
    return df

def gestion_mode_transport(df):
    replace_dict_espagne = {
    'rail': 'train',
    'maritime': 'boat',
    'air': 'plane',
    'bus, rail' : 'bus, train',
    'bus, maritime' : 'bus, boat'
}
    df.loc[df['Pays'] == 'Italie', 'Mode de transport'] = df.loc[df['Pays'] == 'Italie', 'Transportation mode covered'].replace('Other', 'unknown')
    df.loc[df['Pays'] == 'Espagne', 'Mode de transport'] = df.loc[df['Pays'] == 'Espagne', 'Modo de transporte'].replace(replace_dict_espagne)

    return df 

def gestion_theme(df):
    # Fusion des colonnes une par une dans 'Thème du dataset'
    if 'Categoría tipo del conjunto de datos' in df.columns:
        df['Thème du dataset'] = df['Categoría tipo del conjunto de datos']
    
    if 'Thème' in df.columns:
        df['Thème du dataset'] = df['Thème'].combine_first(df['Thème du dataset'])
    
    if 'Category type' in df.columns:
        df['Thème du dataset'] = df['Category type'].combine_first(df['Thème du dataset'])
    
    if 'Thème du jeu de données' in df.columns:
        df['Thème du dataset'] = df['Thème du jeu de données'].combine_first(df['Thème du dataset'])
    
    if 'Theme' in df.columns:
        df['Thème du dataset'] = df['Theme'].combine_first(df['Thème du dataset'])
    
    if 'Tags' in df.columns:
        df['Thème du dataset'] = df['Tags'].combine_first(df['Thème du dataset'])
    
    return df
"""
def granularite_gpt(df):
    # Ajoute une colonne 'Zone couverte' initialement vide
    df['Zone couverte'] = ''
    
    # Remplir la colonne 'Zone couverte' selon les conditions données
    df.loc[df['Pays'] == 'Luxembourg', 'Zone couverte'] = df['Granularité de la couverture territoriale']
    df.loc[df['Pays'] == 'Belgique', 'Zone couverte'] = df['Zone couverte par la publication']
    df.loc[df['Pays'] == 'Italie', 'Zone couverte'] = df['Publié par']
    
    return df

"""
def granularite(df):

    renommage = { 'Belgique' : {'VLAAMS GEWEST' : 'Région Flamande', 
                 'RÉGION DE BRUXELLES-CAPITALE/BRUSSELS HOOFDSTEDELIJK GEWEST' : 'Région Bruxelles-Capitale',
                 'RÉGION DE BRUXELLES-CAPITALE/BRUSSELS HOOFDSTEDELIJK GEWESTVLAAMS GEWESTRÉGION WALLONNE' : 'Pays',
                 'RÉGION DE BRUXELLES-CAPITALE/BRUSSELS HOOFDSTEDELIJK GEWESTRÉGION WALLONNE' : 'Région Bruxelles-Capitale et Wallonne',
                 'RÉGION WALLONNE' : 'Région Wallonne',
                 'RÉGION DE BRUXELLES-CAPITALE/BRUSSELS HOOFDSTEDELIJK GEWESTVLAAMS GEWEST' : 'Région Bruxelles-Capitale et Flamande'},
                'Italie' : {'ATM Milano' : 'Région Lombardia', 'Regione Abruzzo' : 'Région Abruzzo', 'Regione Campania' : 'Région Campania', 'Regione Autonoma Friuli Venezia Giulia' : 'Région Autonome Friuli Venezia Giulia', 'Regione Lazio' : 'Région Lazio', 'Regione Liguria' : 'Région Liguria', 'Regione Marche' : 'Région Marche', 'Regione Piemonte' : 'Région Piemonte', 'Regione Puglia' : 'Région Puglia', 'Regione Emilia-Romagna' : 'Région Emilia-Romagna', 'Regione Toscana' : 'Région Toscana', 'Provincia di Bolzano' : 'Province de Bolzano', 'Trentino Trasporti' : 'Province de Trento', 'Regione Veneto' : 'Région Veneto'},
                'Luxembourg' : {'country' : 'Pays', 'poi' : "Points d'intérêt", 'grande-region' : 'Région', 'lu:commune' : 'Commune'}
    }
    #Granularité de la couverture territoriale (Luxembourg), rien pour l'irlande, rien pour l'espagne, Zone couverte par la publication (Belgique), Publié par (Italie)
    if 'Granularité de la couverture territoriale' in df.columns:
        df['Zone couverte'] = df['Granularité de la couverture territoriale']
    
    if 'Zone couverte par la publication' in df.columns:
        df['Zone couverte'] = df['Zone couverte par la publication'].combine_first(df['Zone couverte'])

    if 'Publié par' in df.columns:
        df.loc[df['Pays'] == 'Italie', 'Zone couverte'] = df.loc[df['Pays'] == 'Italie', 'Publié par']
    
    def map_zone(row):
        country = row['Pays']
        zone = row['Zone couverte']
        if country in renommage and zone in renommage[country]:
            return renommage[country][zone]
        return ''

    df['Zone couverte simplifiée'] = df.apply(map_zone, axis=1)

    return df


def combine_update_dates(df):
    # Liste des colonnes relatives à la date de mise à jour
    update_date_columns = [
        'Date updated', 
        'Dernière mise à jour de ressource', 
        'Date de dernière mise à jour', 
        'metadata_modified', 
        'modified', 
        'date_updated', 
        'Last Updated'
    ]
    
    # Créer une nouvelle colonne "Date de mise à jour" en prenant la première valeur non nulle
    df['Date de mise à jour'] = df[update_date_columns].bfill(axis=1).iloc[:, 0]
    
    # Supprimer les anciennes colonnes utilisées pour cette fusion
    df.drop(columns=update_date_columns, inplace=True)
    
    return df

def combine_creation_dates(df):
    # Liste des colonnes relatives à la date de création
    creation_date_columns = [
        'Date de création', 
        'creationDate', 
        'metadata_created'
    ]
    
    # Créer une nouvelle colonne "Date de création" en prenant la première valeur non nulle
    df['Date de création'] = df[creation_date_columns].bfill(axis=1).iloc[:, 0]
    
    # Supprimer les anciennes colonnes utilisées pour cette fusion
    df.drop(columns=creation_date_columns, inplace=True)
    
    return df

def combine_valid_from_dates(df):
    # Liste des colonnes relatives à la date de début de validité
    valid_from_date_columns = [
        'Valid from', 
        'Válido desde', 
        'Valide depuis', 
        'startDate', 
        'schema:startDate'
    ]
    
    # Créer une nouvelle colonne "Date de début de validité" en prenant la première valeur non nulle
    df['Date de début de validité'] = df[valid_from_date_columns].bfill(axis=1).iloc[:, 0]
    
    # Supprimer les anciennes colonnes utilisées pour cette fusion
    df.drop(columns=valid_from_date_columns, inplace=True)
    
    return df


def combine_valid_until_dates(df):
    # Liste des colonnes relatives à la date de fin de validité
    valid_until_date_columns = [
        'Válido hasta',  
        'endDate', 
        'schema:endDate'
    ]
    
    # Créer une nouvelle colonne "Date de fin de validité" en prenant la première valeur non nulle
    df['Date de fin de validité'] = df[valid_until_date_columns].bfill(axis=1).iloc[:, 0]
    
    # Supprimer les anciennes colonnes utilisées pour cette fusion
    df.drop(columns=valid_until_date_columns, inplace=True)
    
    return df

def combine_data_owner(df):
    # Liste des colonnes relatives au propriétaire des données
    data_owner_columns = [
        'Data Owner', 
        'Data Owner Email', 
        'Data Owner Telephone', 
        'Propriétaire des données',
        'owner_org',
        'contactPoint'
    ]
    
    # Créer une nouvelle colonne "Propriétaire des données" en prenant la première valeur non nulle
    df['Propriétaire des données'] = df[data_owner_columns].bfill(axis=1).iloc[:, 0]
    
    # Supprimer les anciennes colonnes utilisées pour cette fusion
    df.drop(columns=data_owner_columns, inplace=True)
    
    return df

def combine_contact_emails(df):
    # Liste des colonnes relatives aux emails de contact
    contact_email_columns = [
        'E-mail [éditeur]',
        'Email owner',
        'Email publisher',
        'contact-email',
        'hasEmail',
        'mbox',
        'Correo electrónico del Responsable de los metadatos'
    ]
    
    # Créer une nouvelle colonne "Email de contact" en prenant la première valeur non nulle
    df['Email de contact'] = df[contact_email_columns].bfill(axis=1).iloc[:, 0]
    
    # Supprimer les anciennes colonnes utilisées pour cette fusion
    df.drop(columns=contact_email_columns, inplace=True)
    
    return df

def combine_resource_types(df):
    # Liste des colonnes relatives au type de ressource
    resource_type_columns = [
        'Type de ressource', 
        'Tipo de recurso', 
        'Resource type', 
        'Type du jeu de données',
        'NAP type', 
        'Type de NAP', 
        'NeTEx category', 
        'Dataset', 
        'distribution', 
        'theme', 
        'core-dataset', 
        'type'
    ]
    
    # Créer une nouvelle colonne "Type de ressource" en prenant la première valeur non nulle
    df['Type de ressource'] = df[resource_type_columns].bfill(axis=1).iloc[:, 0]
    
    # Supprimer les anciennes colonnes utilisées pour cette fusion
    df.drop(columns=resource_type_columns, inplace=True)
    
    return df

def combine_tags(df):
    # Liste des colonnes relatives aux tags ou mots-clés
    tags_columns = [
        'Tags_italy',
        'Tags_chypre',
        'keywords.en',
        'tags'
    ]
    
    # Créer une nouvelle colonne "Tags" en prenant la première valeur non nulle
    df['Tags'] = df[tags_columns].bfill(axis=1).iloc[:, 0]
    
    # Supprimer les anciennes colonnes utilisées pour cette fusion
    df.drop(columns=tags_columns, inplace=True)
    
    return df

def combine_identifiers(df):
    # Liste des colonnes relatives aux identifiants uniques
    identifier_columns = [
        'ID',
        'adms:identifier',
        'dct:identifier',
        'identifier',
        'System ID'
    ]
    
    # Créer une nouvelle colonne "Identifiant" en prenant la première valeur non nulle
    df['Identifiant'] = df[identifier_columns].bfill(axis=1).iloc[:, 0]
    
    # Supprimer les anciennes colonnes utilisées pour cette fusion
    df.drop(columns=identifier_columns, inplace=True)
    
    return df

def combine_urls(df):
    # Liste des colonnes relatives aux URL
    url_columns = [
        'URL',
        'System URL',
        'Feed URL',
        'accessURL',
        'downloadURL',
        'permalink'
    ]
    
    # Créer une nouvelle colonne "URL" en prenant la première valeur non nulle
    df['URL'] = df[url_columns].bfill(axis=1).iloc[:, 0]
    
    # Supprimer les anciennes colonnes utilisées pour cette fusion
    df.drop(columns=url_columns, inplace=True)
    
    return df

def combine_contact_names(df):
    # Liste des colonnes relatives aux noms de contacts
    contact_name_columns = [
        'Nom [point de contact]',
        'contact-name',
        'foi-name'
    ]
    
    # Créer une nouvelle colonne "Nom du contact" en prenant la première valeur non nulle
    df['Nom du contact'] = df[contact_name_columns].bfill(axis=1).iloc[:, 0]
    
    # Supprimer les anciennes colonnes utilisées pour cette fusion
    df.drop(columns=contact_name_columns, inplace=True)
    
    return df


def combine_phone_numbers(df):
    # Liste des colonnes relatives aux numéros de téléphone
    phone_columns = [
        'Phone Number',
        'contact-phone',
        'foi-phone',
        'Numéro de téléphone [éditeur]',
    ]
    
    # Créer une nouvelle colonne "Téléphone" en prenant la première valeur non nulle
    df['Téléphone'] = df[phone_columns].bfill(axis=1).iloc[:, 0]
    
    # Supprimer les anciennes colonnes utilisées pour cette fusion
    df.drop(columns=phone_columns, inplace=True)
    
    return df



def add_country_code(df):
    # Dictionnaire de correspondance des noms de pays aux codes de pays
    country_code_mapping = {
        'Irlande': 'IE',
        'Luxembourg': 'LU',
        'Espagne': 'ES',
        'Italie': 'IT',
        'Belgique': 'BE',
        'Chypre': 'CY',
        'Suisse': 'CH',
        'UK': 'GB',
        'Germany': 'DE',
        'Poland': 'PL',
        'Norway': 'NO'
    }
    
    # Ajouter la colonne 'Code Pays' en utilisant la correspondance
    df['Code Pays'] = df['Pays'].map(country_code_mapping)
    
    return df
"""

def gestion_score(df):
    #Colonnes concernées : Openness rating (irlande, sous la forme d'étoiles de 0 à 5 étoiles) et Qualité (luxembourg, sous la forme {'all_resources_available': True, 'dataset_description_quality': True, 'has_open_format': True, 'has_resources': True, 'license': True, 'resources_documentation': False, 'score': 0.5555555555555556, 'spatial': True, 'temporal_coverage': False, 'update_frequency': False})
    #on va tout mettre sous la forme d'un score sur 10, mais la question c'est est-ce qu'on transforme un peu les données d'un des deux pays pour faire en sorte que la moyenne soit proche entre les deux pays, en considérant que l'un de deux pays a un système de notation plus dur que l'autre.
    # Filtrer les lignes pour Irlande et Luxembourg

    def normalize_score(value, min_val, max_val):
    #Normalise un score entre 0 et 1
        return (value - min_val) / (max_val - min_val)
    

    # Convertir les valeurs de la colonne 'Openness rating' en nombres, en gérant les erreurs
    df['Openness rating'] = pd.to_numeric(df['Openness rating'], errors='coerce')
    
    # Normaliser les scores d'Irlande (0-5 étoiles) vers 0-1 puis 0-10
    df['Openness rating'] = df['Openness rating'].apply(lambda x: normalize_score(x, 0, 5) * 10 if not np.isnan(x) else np.nan)
    
    # Calculer les scores pour le Luxembourg en multipliant par 10 et arrondissant à l'entier le plus proche
    df['Score Luxembourg'] = df['Qualité'].apply(
        lambda x: round(x['score'] * 10) if isinstance(x, dict) and 'score' in x else np.nan)
    
    # Ajuster les moyennes des scores pour les rendre comparables
    irlande_mean = df.loc[df['Pays'] == 'Irlande', 'Openness rating'].mean()
    luxembourg_mean = df.loc[df['Pays'] == 'Luxembourg', 'Score Luxembourg'].mean()
    
    adjustment_factor = irlande_mean / luxembourg_mean
    
    df.loc[df['Pays'] == 'Luxembourg', 'Score Luxembourg'] *= adjustment_factor
    
    # Fusionner les scores normalisés dans une colonne commune 'Qualité du dataset'
    df['Qualité du dataset'] = df['Openness rating'].combine_first(df['Score Luxembourg'])
    
    # Supprimer les colonnes intermédiaires
    df.drop(columns=['Openness rating', 'Score Luxembourg'], inplace=True)
    
    return df

"""
df=gestion_url(data_frame)
df=formats(df)
df=split_langues(df)
df=liste_des_freq_d_actualisation(df)
df=gestion_licence_2(df)
df=gestion_publie_par(df)
df=gestion_titre(df)
df=gestion_langue(df)
df=gestion_mode_transport(df)
df=gestion_theme(df)
#df=gestion_score(df)
df=granularite(df)
df=combine_update_dates(df)
df=combine_creation_dates(df)
df=combine_valid_from_dates(df)
df=combine_valid_until_dates(df)
df=combine_data_owner(df)
df=combine_contact_emails(df)
df=combine_resource_types(df)
df=combine_tags(df)
df=combine_identifiers(df)
df=combine_urls(df)
df=combine_contact_names(df)
df=combine_phone_numbers(df)
df=add_country_code(df)



#trucs qui marchent pas : 'organization.URL', 'resource type', 'email', \'Valid until\', "Valide jusqu\'à", 'hasTelephone'


#tant qu'à faire, profitions en pour supprimer des colonnes inutiles
df = df.drop(columns=["Unnamed: 0", "Acronyme", "Archivé", "Badges", "Extras", "Propriétaire", "Privé", "Couverture temporelle", "Descripción de los criterios de calidad", "Network coverage", "Date de fin de publication", "Portée du jeu de données"])
#colonnes presque vides
#
df = df.drop(columns=['Categoría tipo del conjunto de datos', 'Catégorie', 'Thème', 'Thème du jeu de données', 'Theme', 'Tags', 'Category type',  "Language", 'Frecuencia de actualización', 'Fréquence de mise à jour', 'Fréquence', 'Update frequency', "Lenguaje de los metadatos", "Lenguaje del conjunto de datos", "Modo de transporte", "Licence", "Licencia de uso", "Descripción de la licencia de uso", "Languages of the dataset", "Transportation mode covered", "Contrat ou licence", "Type de licence"])
#colonnes combinées ou traitées ailleurs





df.to_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/fichiers_concatenes_colonnes_gerees.xlsx', index=False)