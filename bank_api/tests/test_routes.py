import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# Mocking the CRUD functions using pytest-mock
@pytest.fixture
def mock_create_user(mocker):
    return mocker.patch("app.crud.create_user", return_value={"id": 1, "name": "Test User"})


@pytest.fixture
def mock_create_account(mocker):
    return mocker.patch("app.crud.create_account", return_value={"id": 1, "balance": 100.0})


@pytest.fixture
def mock_transfer_money(mocker):
    return mocker.patch("app.crud.transfer_money",
                        return_value={"amount": 50.0, "from_account_id": 1, "to_account_id": 2})


@pytest.fixture
def mock_read_users(mocker):
    return mocker.patch("app.crud.read_users", return_value=[{"id": 1, "name": "John Doe"}])


@pytest.fixture
def mock_read_accounts(mocker):
    return mocker.patch("app.crud.read_accounts", return_value=[{"id": 1, "balance": 100.0}])


@pytest.fixture
def mock_read_account(mocker):
    return mocker.patch("app.crud.read_account", return_value={"id": 1, "balance": 100.0})


@pytest.fixture
def mock_get_transaction_history(mocker):
    return mocker.patch("app.crud.get_transaction_history", return_value=[{"id": 1, "amount": 50.0}])


# Test route for creating user
def test_create_user_route(mock_create_user):
    response = client.post("/users/?name=Test User")
    assert response.status_code == 200


# Test route for creating account
def test_create_account_route(mock_create_account):
    response = client.post("/accounts/1/?initial_balance=100.0")
    assert response.status_code == 200

    # Simulate error
    response = client.post("/accounts/2/?initial_balance=10.0")
    assert response.status_code == 400


# Test route for transferring money
def test_transfer_money_route(mock_transfer_money):
    client.post("/users/?name=Test User")
    client.post("/accounts/1/?initial_balance=1000")
    client.post("/accounts/1/?initial_balance=1000")
    response = client.get("/accounts/")
    account_id_from = response.json()[0]['id']
    account_id_to = response.json()[1]['id']
    response = client.post(f"/transfer/?from_account_id={account_id_from}&to_account_id={account_id_to}&amount=1.0")
    assert response.status_code == 200

    # Simulate error
    mock_transfer_money.side_effect = Exception("Database Error")
    response = client.post(f"/transfer/?from_account_id={account_id_from}&to_account_id={account_id_to}&amount=1100000")
    assert response.status_code == 400


# Test route for getting users
def test_get_users_route(mock_read_users):
    response = client.get("/users/")
    assert response.status_code == 200


# Test route for getting accounts
def test_get_accounts_route(mock_read_accounts):
    response = client.get("/accounts/")
    assert response.status_code == 200


# Test route for getting an account by ID
def test_get_account_route(mock_read_account):
    response = client.get("/accounts/")
    account_id = response.json()[0]['id']

    response = client.get(f"/accounts/{account_id}/")
    assert response.status_code == 200

    # Simulate account not found
    response = client.get("/accounts/999/")
    assert response.status_code == 404


# Test route for getting transaction history
def test_get_transaction_history_route(mock_get_transaction_history):
    response = client.get("/accounts/")
    account_id = response.json()[0]['id']
    response = client.get(f"/transactions/{account_id}/")
    assert response.status_code == 200
