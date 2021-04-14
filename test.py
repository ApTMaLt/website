from requests import delete, get

print(get('http://localhost:5000/api/jobs').json())
print(delete('http://localhost:5000/api/jobs/999').json())
# новости с id = 999 нет в базе
print(delete('http://localhost:5000/api/jobs/q').json())
# id не int
print(delete('http://localhost:5000/api/jobs/1').json())
print(get('http://localhost:5000/api/jobs').json())