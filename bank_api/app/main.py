from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from crud import create_user, create_account  # create
from crud import transfer_money  # update calls
from crud import read_users, read_accounts, read_account, get_transaction_history  # reads

from database import SessionLocal, engine
import models

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency to get the database session for each request
def get_db():
    """
    Dependency that provides a database session to route handlers.

    Yields:
        Session: A database session for the current request.

    Ensures that the session is closed after the request is processed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Route to create a new user
@app.post("/users/")
def add_user(name: str, db: Session = Depends(get_db)):
    """
    Route handler to create a new user.

    Args:
        name (str): The name of the user to be created.
        db (Session): The database session injected by the `get_db` dependency.

    Returns:
        dict: A dictionary containing the details of the newly created user.

    Raises:
        HTTPException: If there is any error during the user creation process.
    """
    try:
        return create_user(db, name)
    except Exception as e:
        raise e


# Route to create a new account for a user
@app.post("/accounts/{user_id}/")
def add_account(user_id: int, initial_balance: float, db: Session = Depends(get_db)):
    """
    Route handler to create a new account for a specific user.

    Args:
        user_id (int): The ID of the user for whom the account is created.
        initial_balance (float): The initial balance for the new account.
        db (Session): The database session injected by the `get_db` dependency.

    Returns:
        dict: A dictionary containing the details of the newly created account.

    Raises:
        HTTPException: If there is any error during the account creation process.
    """
    try:
        return create_account(db, user_id, initial_balance)
    except Exception as e:
        raise e


# Route to transfer money between accounts
@app.post("/transfer/")
def transfer(from_account_id: int, to_account_id: int, amount: float, db: Session = Depends(get_db)):
    """
    Route handler to transfer money from one account to another.

    Args:
        from_account_id (int): The ID of the source account (from which money will be transferred).
        to_account_id (int): The ID of the destination account (to which money will be transferred).
        amount (float): The amount to transfer.
        db (Session): The database session injected by the `get_db` dependency.

    Returns:
        dict: A dictionary containing the details of the transaction.

    Raises:
        HTTPException: If there is an error during the transfer process or if there are insufficient funds.
    """
    try:
        transaction = transfer_money(db, from_account_id, to_account_id, amount)
        if not transaction:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        return transaction
    except Exception as e:
        raise e


# Route to get all users
@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    """
    Route handler to fetch all users.

    Args:
        db (Session): The database session injected by the `get_db` dependency.

    Returns:
        list: A list of dictionaries containing the details of all users.

    Raises:
        HTTPException: If there is any error during the process of fetching users.
    """
    try:
        users = read_users(db)
        return users
    except Exception as e:
        raise e


# Route to get all accounts
@app.get("/accounts/")
def get_accounts(db: Session = Depends(get_db)):
    """
    Route handler to fetch all accounts.

    Args:
        db (Session): The database session injected by the `get_db` dependency.

    Returns:
        list: A list of dictionaries containing the details of all accounts.

    Raises:
        HTTPException: If there is any error during the process of fetching accounts.
    """
    try:
        accounts = read_accounts(db)
        return accounts
    except Exception as e:
        raise e


# Route to get account details by account ID
@app.get("/accounts/{account_id}/")
def get_account(account_id: int, db: Session = Depends(get_db)):
    """
    Route handler to fetch account details for a specific account ID.

    Args:
        account_id (int): The ID of the account to fetch details for.
        db (Session): The database session injected by the `get_db` dependency.

    Returns:
        dict: A dictionary containing the details of the requested account.

    Raises:
        HTTPException: If the account is not found.
    """
    try:
        account = read_account(db, account_id)
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        return account
    except Exception as e:
        raise e


# Route to get transaction history for an account
@app.get("/transactions/{account_id}/")
def get_all_account_transaction_history(account_id: int, db: Session = Depends(get_db)):
    """
    Route handler to fetch the transaction history for a specific account.

    Args:
        account_id (int): The ID of the account to fetch transaction history for.
        db (Session): The database session injected by the `get_db` dependency.

    Returns:
        list: A list of transactions related to the specified account.

    Raises:
        HTTPException: If the account is not found.
    """
    try:
        account = get_transaction_history(db, account_id)
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        return account
    except Exception as e:
        raise e
