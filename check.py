from google import genai 

client = genai.Client(api_key='AIzaSyDpxzen42tGbdTiNzR9gZEiV0jVG5W_THI')
print('Availible models:')
for model in client.models.list():
    print(model.name)
