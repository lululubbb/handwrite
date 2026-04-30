from app import app

with app.test_client() as client:
    response = client.post('/api/user/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test123456'
    })
    print('Status Code:', response.status_code)
    print('Response:', response.get_json())