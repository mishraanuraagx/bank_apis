from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import User, Account, Transaction
import config
from localization import Localization

# Initialize localization for error messages
localizer = Localization(locale="en")


# Create
def create_user(db: Session, name: str):
    """
    Creates a new user in the database.

    Args:
        db (Session): The database session to interact with the database.
        name (str): The name of the user to create.

    Returns:
        User: The created User object.
    """
    db_user = User(name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_account(db: Session, user_id: int, initial_balance: float):
    """
    Creates a new account for a user with an initial balance.

    Args:
        db (Session): The database session to interact with the database.
        user_id (int): The ID of the user for whom the account is being created.
        initial_balance (float): The initial balance to assign to the new account.

    Returns:
        Account: The created Account object.

    Raises:
        HTTPException:
            - If the initial balance is less than or equal to 0, or less than the minimum required balance.
            - If the user with the specified `user_id` does not exist.
    """
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


# Reads
def read_users(db: Session):
    """
    Retrieves all users from the database.

    Args:
        db (Session): The database session to interact with the database.

    Returns:
        List[User]: A list of User objects representing all users in the database.
    """
    users = db.query(User).all()
    return users


def read_accounts(db: Session):
    """
    Retrieves all accounts from the database.

    Args:
        db (Session): The database session to interact with the database.

    Returns:
        List[Account]: A list of Account objects representing all accounts in the database.
    """
    accounts = db.query(Account).all()
    return accounts


def read_account(db: Session, account_id: int):
    """
    Retrieves a specific account from the database by its account ID.

    Args:
        db (Session): The database session to interact with the database.
        account_id (int): The ID of the account to retrieve.

    Returns:
        Account: The Account object corresponding to the `account_id`.

    Raises:
        HTTPException: If no account is found with the given `account_id`.
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail=localizer.get("account_not_found"))
    return account


def get_transaction_history(db: Session, account_id: int):
    """
    Retrieves the transaction history for a specific account.

    Args:
        db (Session): The database session to interact with the database.
        account_id (int): The ID of the account for which to retrieve the transaction history.

    Returns:
        List[Transaction]: A list of Transaction objects related to the account.

    Raises:
        HTTPException: If no account is found with the given `account_id`.
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail=localizer.get("account_not_found"))

    acc_transaction_history = db.query(Transaction).filter((Transaction.from_account_id == account_id) |
                                                           (Transaction.to_account_id == account_id)).all()
    return acc_transaction_history


# Update
def transfer_money(db: Session, from_account_id: int, to_account_id: int, amount: float):
    """
    Transfers money from one account to another, ensuring sufficient balance.

    Args:
        db (Session): The database session to interact with the database.
        from_account_id (int): The ID of the source account from which money is being transferred.
        to_account_id (int): The ID of the destination account to which money is being transferred.
        amount (float): The amount to transfer between the two accounts.

    Returns:
        Transaction: A Transaction object representing the transfer.

    Raises:
        HTTPException:
            - If the source or destination account is invalid (does not exist).
            - If there are insufficient funds in the source account.
    """
    db_from_account = db.query(Account).filter(Account.id == from_account_id).first()
    db_to_account = db.query(Account).filter(Account.id == to_account_id).first()

    # Check source account
    if db_from_account is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=localizer.get("invalid_account_from")
        )

    # Check destination account
    if db_to_account is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=localizer.get("invalid_account_to")
        )

    # Check if sufficient balance is available for transfer
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
