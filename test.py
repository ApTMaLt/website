from requests import get, delete

print(get('http://localhost:5000/api/users/1').json())