import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import User, Account
from sqlalchemy.orm import Session

# Create the test client
client = TestClient(app)

# Fixture for creating a database session for each test
@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to create a user for testing
def create_user_for_test(db: Session, name="Test User"):
    user = User(name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Helper function to create an account for testing
def create_account_for_test(db: Session, user_id: int, initial_balance=100.0):
    account = Account(user_id=user_id, balance=initial_balance)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

# Test case for creating a user
def test_create_user_route(db_session):
    # Test normal user creation
    response = client.post("/users/?name=Jane Doe")
    assert response.status_code == 200

    # Test user creation with an empty name (should fail)
    response = client.post("/users/?name=")
    assert response.status_code == 422  # 422 Unprocessable Entity

# Test case for creating an account
def test_create_account_route(db_session):
    user = create_user_for_test(db_session)

    # Test creating an account with a valid initial balance
    response = client.post(f"/accounts/{user.id}/?initial_balance=100")
    assert response.status_code == 200
    assert response.json()["balance"] == 100.0

    # Test creating an account with an invalid balance (less than the minimum balance)
    response = client.post(f"/accounts/{user.id}/?initial_balance=5")
    assert response.status_code == 400  # Should return 400 for invalid balance

    # Test creating an account with a non-existent user
    response = client.post("/accounts/999/?initial_balance=100")
    assert response.status_code == 400  # Should return 400 for user not found

# Test case for transferring money between accounts
def test_transfer_money_route(db_session):
    user1 = create_user_for_test(db_session)
    user2 = create_user_for_test(db_session)

    account1 = create_account_for_test(db_session, user_id=user1.id, initial_balance=100.0)
    account2 = create_account_for_test(db_session, user_id=user2.id, initial_balance=50.0)

    # Test valid transfer
    response = client.post("/transfer/?from_account_id=1&to_account_id=2&amount=50")
    assert response.status_code == 200
    assert response.json()["amount"] == 50.0

    # Test insufficient balance for transfer
    response = client.post("/transfer/?from_account_id=1&to_account_id=2&amount=200")
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient balance"

    # Test invalid "from" account
    response = client.post("/transfer/?from_account_id=999&to_account_id=2&amount=50")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid account from"

    # Test invalid "to" account
    response = client.post("/transfer/?from_account_id=1&to_account_id=999&amount=50")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid account to"

# Test case for getting users
def test_get_users_route(db_session):
    create_user_for_test(db_session, name="John Doe")

    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "John Doe"

# Test case for getting accounts
def test_get_accounts_route(db_session):
    user = create_user_for_test(db_session)
    create_account_for_test(db_session, user_id=user.id, initial_balance=100.0)

    response = client.get("/accounts/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["balance"] == 100.0

# Test case for getting a single account
def test_get_account_route(db_session):
    user = create_user_for_test(db_session)
    account = create_account_for_test(db_session, user_id=user.id, initial_balance=100.0)

    response = client.get(f"/accounts/{account.id}/")
    assert response.status_code == 200
    assert response.json()["balance"] == 100.0

    # Test getting a non-existing account
    response = client.get("/accounts/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"

# Test case for getting transaction history for an account
def test_get_transaction_history_route(db_session):
    user = create_user_for_test(db_session)
    account = create_account_for_test(db_session, user_id=user.id, initial_balance=100.0)

    # Test getting transaction history for the account
    response = client.get(f"/transactions/{account.id}/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    # Test getting transaction history for a non-existing account
    response = client.get("/transactions/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"
