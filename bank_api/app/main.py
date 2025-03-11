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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create User
@app.post("/users/")
def add_user(name: str, db: Session = Depends(get_db)):
    try:
        return create_user(db, name)
    except Exception as e:
        raise e


# Create Account
@app.post("/accounts/{user_id}/")
def add_account(user_id: int, initial_balance: float, db: Session = Depends(get_db)):
    try:
        return create_account(db, user_id, initial_balance)
    except Exception as e:
        raise e


# Transfer Money
@app.post("/transfer/")
def transfer(from_account_id: int, to_account_id: int, amount: float, db: Session = Depends(get_db)):
    try:
        transaction = transfer_money(db, from_account_id, to_account_id, amount)
        if not transaction:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        return transaction
    except Exception as e:
        raise e


# Read
# Get all list, given these endpoints are for dedicated managers to users for a bank branch
@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    try:
        users = read_users(db)
        return users
    except Exception as e:
        raise e


@app.get("/accounts/")
def get_accounts(db: Session = Depends(get_db)):
    try:
        accounts = read_accounts(db)
        return accounts
    except Exception as e:
        raise e


@app.get("/accounts/{account_id}/")
def get_account(account_id: int, db: Session = Depends(get_db)):
    try:
        account = read_account(db, account_id)
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        return account
    except Exception as e:
        raise e


@app.get("/transactions/{account_id}/")
def get_all_account_transaction_history(account_id: int, db: Session = Depends(get_db)):
    try:
        account = get_transaction_history(db, account_id)
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        return account
    except Exception as e:
        raise e
