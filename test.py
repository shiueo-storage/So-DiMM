import requests

API_HOST = 'https://kaist.me/api/ksa/DS/api.php'
params = {'apiName': ['list']}

u = response = requests.post(API_HOST, params=params)
print(u.json())


