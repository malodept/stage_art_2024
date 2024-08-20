# stage_art_2024

Ce projet  consiste dans une première partie en l'élaboration d'un dataset avec en colonnes des noms de métadonnées et en lignes des jeux de données disponibles. L'objectif est d'extraire les métadonnées de tous les datasets sur des sujets de transport mis à disposition par les différents points d'accès nationaux des pays de l'Union Européenne.

Pour chaque pays, on cherche certaines informations comme la fréquence d'actualisation des données, la licence utilisée, le mode de transport concerné ou encore la granularité territoriale correspondant au jeu de données. On pourra ensuite réaliser des visualisations sur Power BI pour comparer la situation entre les différents pays.

Losqu'elle est fournie, on utilisera l'API donnée par le pays, ou bien le fichier json disponible dans les requêtes de la page. Sinon, en dernier recours, on scrappera la page html en essayer de chercher les bonnes métadonnées dans les bonnes balises.

On utilisera aussi le modèle Llama de Meta AI en passant par l'application GPT4ALL pour trouver des informations qui ne sont pas directement disponibles.

Après avoir collecté les données, une partie nécessaire est le traitement des données pour assurer la pertinence des analyses. On pourra alors trouver dans gestion_colonnes.py l'ensemble du processus de gestion des colonnes, principalement la fusion de colonnes, le renommage de données, et l'uniformisation de données qui pourraient différer entre les pays.

Réalisé par Malo de Pastor à l'Autorité de Régulation des Transports, au sein de la direction de l'observation des marchés (du 24 juin 2024 au 23 août 2024)
