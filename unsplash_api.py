# https://api.unsplash.com/search/photos?page=1&query=SEARCH_QUERY
import requests

geocoder_request = ["https://api.unsplash.com/photos/random?client_id=NGbcLeb-P3bs4CN6I9nxdkQw36zNSnCNz7tF-zGOIws&count=15",]
for i in geocoder_request:
    response = requests.get(i)
    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
        print(json_response)
    else:
        print(response)