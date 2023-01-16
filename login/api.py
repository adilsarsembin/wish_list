import requests

FILM = 'Invincibles'
API_KEY = '76a87b17f0e9e54d945469d5f94c074f'
URL = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={FILM}'

results = requests.get(URL).json()['results']

for result in results:
    print(result['original_title'])