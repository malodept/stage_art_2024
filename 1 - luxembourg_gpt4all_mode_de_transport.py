#ça ne fonctionnait pas hors d'un notebook
from gpt4all import GPT4All
import pandas as pd

model = GPT4All(model_name="Meta-Llama-3-8B-Instruct.Q4_0.gguf", model_path="P:/gpt4all/")

chemin_luxembourg = 'C:/Users/m-de-pastor/Desktop/Un peut tout/luxembourg.xlsx'
df_luxembourg = pd.read_excel(chemin_luxembourg)

def predict_mode(row, session):
    titre = row['Titre']
    tags = row['Tags']
    description = row['Description']
    
    prompt = f"What is the most appropriate mode of transport between 'car', 'bus', 'train', 'plane', 'boat', 'cycle', and 'unknown' given the following information?\n\nTitle: {titre}\nTags: {tags}\nDescription: {description}\n\nPlease respond with a single word from the provided options.\n\nMode of transport:"
    
    response = session.generate(prompt, max_tokens=1024)
    
    mode_of_transport = response.split('Mode of transport:')[-1].strip().lower()
    
    return mode_of_transport

with model.chat_session() as session:
    df_luxembourg['Mode de transport'] = df_luxembourg.apply(lambda row: predict_mode(row, session), axis=1)

df_luxembourg.to_excel('C:/Users/m-de-pastor/Desktop/Un peut tout/luxembourg_transfo_3_gpt4all.xlsx', index=False)






