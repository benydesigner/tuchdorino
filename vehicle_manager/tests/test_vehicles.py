import pytest
import os # For generating unique names if needed
from fastapi.testclient import TestClient

# client, auth_headers, test_db_setup_and_teardown, test_user_and_token
# are fixtures from conftest.py

def test_create_vehicle(client, auth_headers, test_db_setup_and_teardown, test_user_and_token):
    vehicle_data = {
        'make': 'TestMake', 'model': 'TestModel', 'year': 2022,
        'license_plate': f'TEST{os.urandom(3).hex().upper()}', 'odometer_reading': 1000
    }
    response = client.post('/api/v1/vehicles/', json=vehicle_data, headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['make'] == vehicle_data['make']
    assert data['license_plate'] == vehicle_data['license_plate']
    assert 'id' in data
    assert data['owner_id'] == test_user_and_token['user_id'] # Verify owner_id

    response_no_auth = client.post('/api/v1/vehicles/', json=vehicle_data)
    assert response_no_auth.status_code == 401

def test_read_all_vehicles_owned_by_user(client, auth_headers, test_user_and_token, test_db_setup_and_teardown):
    # Create a vehicle first for this user
    plate1 = f'OWNED{os.urandom(3).hex().upper()}'
    vehicle_data_1 = {'make': 'MyCar', 'model': 'ModelX', 'year': 2023, 'license_plate': plate1, 'odometer_reading': 500}
    cr_resp = client.post('/api/v1/vehicles/', json=vehicle_data_1, headers=auth_headers)
    assert cr_resp.status_code == 200, cr_resp.text

    response = client.get('/api/v1/vehicles/', headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    found = any(v['license_plate'] == plate1 and v['owner_id'] == test_user_and_token['user_id'] for v in data)
    assert found, f'Vehicle with plate {plate1} not found in response for the correct owner'

def test_read_single_vehicle(client, auth_headers, test_user_and_token, test_db_setup_and_teardown):
    plate = f'UNIQUE{os.urandom(3).hex().upper()}'
    vehicle_data = {'make': 'UniqueMake', 'model': 'UniqueModel', 'year': 2024, 'license_plate': plate, 'odometer_reading': 100}
    create_response = client.post('/api/v1/vehicles/', json=vehicle_data, headers=auth_headers)
    assert create_response.status_code == 200, create_response.text
    vehicle_id = create_response.json()['id']

    response = client.get(f'/api/v1/vehicles/{vehicle_id}', headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['id'] == vehicle_id
    assert data['license_plate'] == plate
    assert data['owner_id'] == test_user_and_token['user_id']

    response_non_existent = client.get(f'/api/v1/vehicles/{vehicle_id + 999}', headers=auth_headers)
    assert response_non_existent.status_code == 404

    response_no_auth = client.get(f'/api/v1/vehicles/{vehicle_id}')
    assert response_no_auth.status_code == 401

def test_update_vehicle(client, auth_headers, test_user_and_token, test_db_setup_and_teardown):
    plate = f'UPDATE{os.urandom(3).hex().upper()}'
    vehicle_data = {'make': 'UpdateMake', 'model': 'UpdateModel', 'year': 2021, 'license_plate': plate, 'odometer_reading': 2000}
    create_response = client.post('/api/v1/vehicles/', json=vehicle_data, headers=auth_headers)
    assert create_response.status_code == 200, create_response.text
    vehicle_id = create_response.json()['id']

    update_data = {'odometer_reading': 2500, 'model': 'UpdatedModelX'}
    response = client.put(f'/api/v1/vehicles/{vehicle_id}', json=update_data, headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['odometer_reading'] == 2500
    assert data['model'] == 'UpdatedModelX'
    assert data['owner_id'] == test_user_and_token['user_id']

    response_non_existent = client.put(f'/api/v1/vehicles/{vehicle_id + 999}', json=update_data, headers=auth_headers)
    assert response_non_existent.status_code == 404

    response_no_auth = client.put(f'/api/v1/vehicles/{vehicle_id}', json=update_data)
    assert response_no_auth.status_code == 401

def test_delete_vehicle(client, auth_headers, test_db_setup_and_teardown):
    plate = f'DELETE{os.urandom(3).hex().upper()}'
    vehicle_data = {'make': 'DeleteMake', 'model': 'DeleteModel', 'year': 2020, 'license_plate': plate, 'odometer_reading': 3000}
    create_response = client.post('/api/v1/vehicles/', json=vehicle_data, headers=auth_headers)
    assert create_response.status_code == 200, create_response.text
    vehicle_id = create_response.json()['id']

    response = client.delete(f'/api/v1/vehicles/{vehicle_id}', headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['id'] == vehicle_id

    get_response = client.get(f'/api/v1/vehicles/{vehicle_id}', headers=auth_headers)
    assert get_response.status_code == 404

    response_non_existent = client.delete(f'/api/v1/vehicles/{vehicle_id + 999}', headers=auth_headers)
    assert response_non_existent.status_code == 404

    # Test deleting already deleted item or no auth (will be caught by 401 first if no auth)
    # response_no_auth = client.delete(f'/api/v1/vehicles/{vehicle_id}') # ID is gone
    # assert response_no_auth.status_code == 401 # This check is fine for auth path

def test_vehicle_access_by_different_user(client, test_db_setup_and_teardown, test_user_and_token):
    main_user_auth_headers = {'Authorization': f'Bearer {test_user_and_token["token"]}'}

    plate_main = f'MAIN{os.urandom(3).hex().upper()}'
    vehicle_data = {'make': 'MainUserCar', 'model': 'MUC', 'year': 2020, 'license_plate': plate_main, 'odometer_reading': 100}
    create_resp = client.post('/api/v1/vehicles/', json=vehicle_data, headers=main_user_auth_headers)
    assert create_resp.status_code == 200, create_resp.text
    main_user_vehicle_id = create_resp.json()['id']

    other_user_email = f'other_{os.urandom(4).hex()}@example.com'
    other_user_password = 'otherpassword'
    reg_resp = client.post('/api/v1/auth/register', json={'email': other_user_email, 'password': other_user_password})
    assert reg_resp.status_code == 200, reg_resp.text

    login_resp = client.post('/api/v1/auth/token', data={'username': other_user_email, 'password': other_user_password})
    assert login_resp.status_code == 200, login_resp.text
    other_user_token = login_resp.json()['access_token']
    other_user_auth_headers = {'Authorization': f'Bearer {other_user_token}'}

    response_get = client.get(f'/api/v1/vehicles/{main_user_vehicle_id}', headers=other_user_auth_headers)
    assert response_get.status_code == 403

    response_put = client.put(f'/api/v1/vehicles/{main_user_vehicle_id}', json={'odometer_reading': 999}, headers=other_user_auth_headers)
    assert response_put.status_code == 403

    response_delete = client.delete(f'/api/v1/vehicles/{main_user_vehicle_id}', headers=other_user_auth_headers)
    assert response_delete.status_code == 403
