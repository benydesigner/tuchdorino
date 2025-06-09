import pytest
from fastapi.testclient import TestClient
# from app.main import app # client fixture provides this
# from app.schemas import User # For response validation

# client fixture is automatically available from conftest.py

def test_read_root(client): # New test for root path
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Vehicle Manager API"}

def test_register_user(client, test_db_setup_and_teardown): # use test_db_setup_and_teardown for clean state
    response = client.post('/api/v1/auth/register', json={'email': 'newuser@example.com', 'password': 'newpassword'})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['email'] == 'newuser@example.com'
    assert 'id' in data
    assert data['is_active'] == True

    # Test duplicate email
    response_dup = client.post('/api/v1/auth/register', json={'email': 'newuser@example.com', 'password': 'anotherpassword'})
    assert response_dup.status_code == 400
    assert response_dup.json()['detail'] == 'Email already registered'

def test_login_for_access_token(client, test_user_and_token, test_db_setup_and_teardown):
    # test_user_and_token fixture already creates a user and logs them in once to get a token.
    # This test primarily verifies the login endpoint with correct and incorrect credentials.
    user_email = test_user_and_token['user']['email']
    user_password = test_user_and_token['user']['password']

    response = client.post('/api/v1/auth/token', data={'username': user_email, 'password': user_password})
    assert response.status_code == 200, response.text
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'

    response_incorrect_pw = client.post('/api/v1/auth/token', data={'username': user_email, 'password': 'wrongpassword'})
    assert response_incorrect_pw.status_code == 401
    assert response_incorrect_pw.json()['detail'] == 'Incorrect email or password'

    response_incorrect_email = client.post('/api/v1/auth/token', data={'username': 'wrong@example.com', 'password': user_password})
    assert response_incorrect_email.status_code == 401
    assert response_incorrect_email.json()['detail'] == 'Incorrect email or password'


def test_read_users_me(client, auth_headers, test_user_and_token, test_db_setup_and_teardown):
    # auth_headers uses the token from test_user_and_token
    response = client.get('/api/v1/auth/users/me', headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['email'] == test_user_and_token['user']['email']

    response_no_token = client.get('/api/v1/auth/users/me')
    assert response_no_token.status_code == 401 # Default is 403 if no token, but OAuth2PasswordBearer makes it 401
    # FastAPI's default for OAuth2PasswordBearer if token is missing or invalid is 401,
    # with detail "Not authenticated" if no token, or "Could not validate credentials" if token is invalid.
    assert response_no_token.json()['detail'] == 'Not authenticated'
