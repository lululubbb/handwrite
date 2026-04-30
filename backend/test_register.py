import requests
import json

url = 'http://localhost:5000/api/user/register'
headers = {'Content-Type': 'application/json'}
data = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'Test123456'
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print('Status Code:', response.status_code)
print('Response:', response.json())