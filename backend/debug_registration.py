from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
response = client.post('/users/register', json={'username':'debuguser','email':'debug@example.com','password':'secret123'})
print('status', response.status_code)
print(response.text)
