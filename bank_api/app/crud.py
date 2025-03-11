from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import User, Account, Transaction
import config
from localization import Localization

localizer = Localization(locale="en")


# Create
def create_user(db: Session, name: str):
    db_user = User(name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_account(db: Session, user_id: int, initial_balance: float):
    if initial_balance <= 0 or initial_balance < config.MIN_ACCOUNT_BALANCE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=localizer.get("min_balance_error", min_balance=config.MIN_ACCOUNT_BALANCE)
        )
    user_exist = db.query(User).filter(User.id == user_id).first()
    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=localizer.get("user_not_found")
        )

    db_account = Account(user_id=user_id, balance=initial_balance)

    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


# reads
def read_users(db: Session):
    users = db.query(User).all()
    return users


def read_accounts(db: Session):
    accounts = db.query(Account).all()
    return accounts


def read_account(db: Session, account_id: int):
    account = db.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail=localizer.get("account_not_found"))
    return account


def get_transaction_history(db: Session, account_id: int):
    account = db.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail=localizer.get("account_not_found"))

    acc_transaction_history = db.query(Transaction).filter((Transaction.from_account_id == account_id) |
                                                           (Transaction.to_account_id == account_id)).all()
    return acc_transaction_history


# update
def transfer_money(db: Session, from_account_id: int, to_account_id: int, amount: float):
    db_from_account = db.query(Account).filter(Account.id == from_account_id).first()
    db_to_account = db.query(Account).filter(Account.id == to_account_id).first()

    # check account from
    if db_from_account is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=localizer.get("invalid_account_from")
        )
    # check account to
    if db_to_account is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=localizer.get("invalid_account_to")
        )

    # check min balance maintained after transfer
    if db_from_account.balance >= amount + config.MIN_ACCOUNT_BALANCE:
        db_from_account.balance -= amount
        db_to_account.balance += amount
        transaction = Transaction(amount=amount, from_account_id=from_account_id, to_account_id=to_account_id)
        db.add(transaction)
        db.commit()
        db.refresh(db_from_account)
        db.refresh(db_to_account)
        return transaction
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=localizer.get("transfer_not_possible_min_bal", min_balance=config.MIN_ACCOUNT_BALANCE,
                                 currency=config.CURRENCY_SHORT)
        )
