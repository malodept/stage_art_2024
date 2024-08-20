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

excel_files = ['C:/Users/m-de-pastor/Desktop/Un peut tout/ireland_test.xlsx', 
               'C:/Users/m-de-pastor/Desktop/Un peut tout/luxembourg_transfo_3_gpt4all.xlsx', 
               'C:/Users/m-de-pastor/Desktop/Un peut tout/espagne_transfo.xlsx',  #j'avais un fichier transformation.py qui découpait la table be es lu it, mais en fait il est plus intéressant de faire un fichier par pays et ensuite concaténer et ensuite traiter les colonnes
               'C:/Users/m-de-pastor/Desktop/Un peut tout/italie_transfo.xlsx', 
               'C:/Users/m-de-pastor/Desktop/Un peut tout/belgique_transfo.xlsx',
               'C:/Users/m-de-pastor/Desktop/Un peut tout/chypre.xlsx',
               'C:/Users/m-de-pastor/Desktop/Un peut tout/suisse.xlsx',
               'C:/Users/m-de-pastor/Desktop/Un peut tout/uk.xlsx',
               'C:/Users/m-de-pastor/Desktop/Un peut tout/germany.xlsx',
               'C:/Users/m-de-pastor/Desktop/Un peut tout/poland_transport_datasets.xlsx',
               'C:/Users/m-de-pastor/Desktop/Un peut tout/norvege.xlsx'
               ]

pays = ['Irlande', 'Luxembourg', 'Espagne', 'Italie', 'Belgique', 'Chypre', 'Suisse', 'UK', 'Germany', 'Poland', 'Norway']

dfs = []
for file, country in zip(excel_files, pays):        #ajout d'une colonne pays
    df = pd.read_excel(file)
    df['Pays'] = country  
    dfs.append(df)

merged_df = pd.concat(dfs, ignore_index=True)

merged_df.reset_index(inplace=True) #ajout d'une colonne index, plus simple à gérer qu'un titre

merged_df.to_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/fichiers_concatenes.xlsx', index=False)
