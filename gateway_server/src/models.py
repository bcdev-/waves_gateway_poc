import logging
import datetime
import time
import random
import string
from . import cfg, Base
from extensions.banking_models import AccountExt, BankDepositExt, BankWithdrawalExt
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Boolean
from sqlalchemy.orm.session import Session


class Account(Base, AccountExt):
    __tablename__ = 'accounts'

    def __init__(self, address, public_key, deposit_address):
        AccountExt.__init__(self)
        self.address = address
        self.public_key = public_key
        self.deposit_address = deposit_address

    # TODO: Active&Inactive account
    address = Column(String, unique=True, primary_key=True)
    public_key = Column(String, unique=True)
    deposit_address = Column(String, unique=True)

    def __repr__(self):
        return "<Account(public_key='%s', address='%s')>" % (
                         self.public_key, self.address)


class Balance(Base):
    __tablename__ = 'balances'

    def __init__(self, address, currency):
        self.address = address
        self.currency = currency

    address = Column(String, ForeignKey('accounts.address'), primary_key=True)
    currency = Column(String, primary_key=True)
    balance = Column(BigInteger, default=0)
    withdraw_to_blockchain_balance = Column(BigInteger, default=0)
    withdraw_to_blockchain_automatically = Column(Boolean, default=True)

    @staticmethod
    def get_all_balances(session: Session, account: Account):
        balances = session.query(Balance).filter_by(address=account.address).all()
        final_balances = []
        missing_currencies = set([id["id"] for id in cfg.assets])
        for balance in balances:
            if balance.currency not in missing_currencies:
                logging.warning("Currency %s is not defined in configuration!" % balance.currency)
            else:
                missing_currencies.remove(balance.currency)
                final_balances.append(balance)

        for currency in missing_currencies:
            logging.debug("Adding balance to DB: %s %s" % (account.address, currency))
            balance = Balance(account.address, currency)
            final_balances.append(balance)
            # TODO: Temporary! The only part that commits ANY balances should be a blockchain manager!
            session.add(balance)
            session.commit()
        return final_balances


class BlockchainTransaction(Base):
    __tablename__ = 'blockchain_transactions'

    def __init__(self, transaction_id, address, type, timestamp, currency=None, amount=None):
        self.transaction_id = transaction_id
        self.address = address
        self.type = type
        self.currency = currency
        self.amount = amount
        self.timestamp = timestamp

    # TODO: Block [confirmations]
    transaction_id = Column(String, primary_key=True)
    address = Column(String, ForeignKey('accounts.address'), index=True)
    type = Column(Integer)
    timestamp = Column(BigInteger)
    currency = Column(String, nullable=True)
    amount = Column(BigInteger, nullable=True)

    already_accounted = Column(Boolean, default=False, index=True)

    @property
    def timestamp_readable(self):
        return datetime.datetime.fromtimestamp(self.timestamp / 1000.).strftime('%d.%m.%Y %H:%M:%S')

    @staticmethod
    def get_all_transactions(session: Session, account: Account):
        return session.query(BlockchainTransaction).filter_by(address=account.address).all()


class BankDeposit(Base, BankDepositExt):
    __tablename__ = 'bank_deposit'

    def __init__(self, address, currency, amount, *args, **kwargs):
        self.address = address
        self.currency = currency
        self.amount = amount
        BankDepositExt.__init__(self, *args, **kwargs)

    @staticmethod
    def get_all(session: Session, account: Account) -> list:
        return session.query(BankDeposit).filter_by(address=account.address).all()

    address = Column(String, ForeignKey('accounts.address'), index=True)
    # Blockchain asset ID
    currency = Column(String)
    amount = Column(BigInteger)

    already_accounted = Column(Boolean, default=False, index=True)
    waves_transaction_id = Column(String, nullable=True, default=None)


class BankWithdrawal(Base, BankWithdrawalExt):
    __tablename__ = 'bank_withdrawal'

    address = Column(String, ForeignKey('accounts.address'), index=True)
    # Blockchain asset ID
    currency = Column(String)
    amount = Column(BigInteger)

    already_accounted = Column(Boolean, default=False, index=True)


class WACSession(Base):
    __tablename__ = 'wac_sessions'
    SESSION_ID_LENGTH = 64

    def __init__(self, address, asset_id):
        self.address = address
        self.asset_id = asset_id
        self.timeout = int(time.time()) + cfg.session_timeout
        self.session_id = ''.join(random.choice(string.digits + string.ascii_uppercase + string.ascii_lowercase)
                                  for _ in range(self.SESSION_ID_LENGTH))

    session_id = Column(String, primary_key=True)
    address = Column(String, ForeignKey('accounts.address'))
    timeout = Column(BigInteger, index=True)
    asset_id = Column(String)

    @staticmethod
    def truncate_old():
        # TODO
        pass
