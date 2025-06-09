import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool # Recommended for SQLite in-memory for tests
import os
# import sys # Removed sys.path manipulation

# Assuming pytest is run from vehicle_manager directory,
# 'app' should be importable directly.
from app.main import app
from app.core.database import Base, get_db
from app.models import User as UserModel
from app.core.security import get_password_hash


# --- Test Database Setup (In-Memory SQLite) ---
SQLALCHEMY_DATABASE_URL_TEST = 'sqlite:///:memory:' # In-memory SQLite

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL_TEST,
    connect_args={'check_same_thread': False}, # Needed for SQLite
    poolclass=StaticPool # Ensures same connection for in-memory DB
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope='function')
def test_db_setup_and_teardown():
    Base.metadata.create_all(bind=engine_test) # Ensure tables are created
    yield
    Base.metadata.drop_all(bind=engine_test) # Clean up: drop all tables

@pytest.fixture(scope='function')
def db_session(test_db_setup_and_teardown):
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope='function')
def test_user_and_token(client, test_db_setup_and_teardown):
    user_data = {'email': f'testuser_{os.urandom(4).hex()}@example.com', 'password': 'testpassword'}

    temp_db = TestingSessionLocal()
    try:
        existing_user = temp_db.query(UserModel).filter(UserModel.email == user_data['email']).first()
        if not existing_user:
            hashed_password = get_password_hash(user_data['password'])
            db_user = UserModel(email=user_data['email'], hashed_password=hashed_password, is_active=True)
            temp_db.add(db_user)
            temp_db.commit()
        else:
            if not existing_user.is_active:
                existing_user.is_active = True
                temp_db.commit()
    finally:
        temp_db.close()

    login_response = client.post('/api/v1/auth/token', data={'username': user_data['email'], 'password': user_data['password']})

    if login_response.status_code != 200:
        # Try to register if login failed (e.g. user not in DB for client session)
        # This also helps debug if registration itself is the issue.
        reg_response = client.post('/api/v1/auth/register', json=user_data)
        # If registration was successful (200) or user already existed (400 from this attempt), try login again
        if reg_response.status_code == 200 or (reg_response.status_code == 400 and "Email already registered" in reg_response.text):
             login_response = client.post('/api/v1/auth/token', data={'username': user_data['email'], 'password': user_data['password']})
        else: # Registration itself failed with an unexpected error
            assert False, f"Fallback registration failed. Reg Path: /api/v1/auth/register. Status: {reg_response.status_code}. Response: {reg_response.text}"


    assert login_response.status_code == 200, f'Failed to log in test user: {login_response.text}. Email: {user_data["email"]}'
    token = login_response.json()['access_token']

    user_info_response = client.get('/api/v1/auth/users/me', headers={'Authorization': f'Bearer {token}'})
    assert user_info_response.status_code == 200, f'Failed to get user_me for token. Response: {user_info_response.text}'
    user_id = user_info_response.json()['id']

    return {'user': user_data, 'token': token, 'user_id': user_id}


@pytest.fixture(scope='function')
def auth_headers(test_user_and_token):
    return {'Authorization': f'Bearer {test_user_and_token["token"]}'}
