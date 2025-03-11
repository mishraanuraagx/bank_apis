from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)  # Specify length here
    accounts = relationship("Account", back_populates="owner")


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates="accounts")

    # Relationships for transactions
    transactions_from = relationship("Transaction", foreign_keys="[Transaction.from_account_id]",
                                     back_populates="from_account")
    transactions_to = relationship("Transaction", foreign_keys="[Transaction.to_account_id]",
                                   back_populates="to_account")


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    from_account_id = Column(Integer, ForeignKey('accounts.id'))
    to_account_id = Column(Integer, ForeignKey('accounts.id'))

    # Relationship with Account: outgoing (from) and incoming (to)
    from_account = relationship("Account", foreign_keys=[from_account_id], back_populates="transactions_from")
    to_account = relationship("Account", foreign_keys=[to_account_id], back_populates="transactions_to")
