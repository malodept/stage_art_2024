#ça ne fonctionnait pas hors d'un notebook
from gpt4all import GPT4All
import pandas as pd

model = GPT4All(model_name="Meta-Llama-3-8B-Instruct.Q4_0.gguf", model_path="P:/gpt4all/")

chemin_irlande = 'C:/Users/m-de-pastor/Desktop/Un peut tout/ireland_test.xlsx'
df_irlande = pd.read_excel(chemin_irlande)

def predict_mode(row, session):
    titre = row['Titre']
    
    prompt = f"What is the most appropriate mode of transport between 'car', 'bus', 'train', 'plane', 'boat', 'cycle', and 'unknown' given the following information?\n\nTitle: {titre}\n\nPlease respond with a single word from the provided options.\n\nMode of transport:"
    
    response = session.generate(prompt, max_tokens=1024)
    
    mode_of_transport = response.split('Mode of transport:')[-1].strip().lower()
    
    return mode_of_transport

with model.chat_session() as session:
    df_irlande['Mode de transport'] = df_irlande.apply(lambda row: predict_mode(row, session), axis=1)

df_irlande.to_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/irlande_test_avec_gpt4all.xlsx', index=False)