import logging
import datetime
import time
import random
import string
import json
from . import cfg, Base
from extensions.banking_models import AccountExt, BankDepositExt, BankWithdrawalExt
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Boolean
from sqlalchemy.orm.session import Session
from .currency import currencies


class Account(Base, AccountExt):
    __tablename__ = 'accounts'

    def __init__(self, address, public_key, deposit_address, *args, **kwargs):
        self.address = address
        self.public_key = public_key
        self.deposit_address = deposit_address
        AccountExt.__init__(self, *args, **kwargs)

    # TODO: Active&Inactive account
    address = Column(String, unique=True, primary_key=True)
    public_key = Column(String, unique=True)
    deposit_address = Column(String, unique=True)

    def __repr__(self):
        return "<Account(public_key='%s', address='%s')>" % (
            self.public_key, self.address)


# if incoming_blockchain_transaction->attachment == bank_withdrawal->attachment:
#   process_withdrawal
# else:
#   send_back_refund
# TODO: Rename to IncomingTransaction... Or WithdrawalTransaction
class BlockchainTransaction(Base):
    __tablename__ = 'blockchain_transactions'

    def __init__(self, transaction_id, address, type, timestamp, attachment, currency=None, amount=None):
        self.transaction_id = transaction_id
        self.address = address
        self.type = type
        self.currency = currency
        self.amount = amount
        self.timestamp = timestamp
        self.attachment = attachment

    # TODO: Block [confirmations]
    transaction_id = Column(String, primary_key=True)
    # TODO: Rename address to user
    address = Column(String, ForeignKey('accounts.address'), index=True)
    type = Column(Integer)
    timestamp = Column(BigInteger)
    currency = Column(String, nullable=True)
    amount = Column(BigInteger, nullable=True)
    attachment = Column(String, index=True)

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

    @property
    def currency_name(self) -> str:
        if self.currency in currencies:
            return currencies[self.currency].name
        return "UnknownCurrency<%s>" % self.currency

    @property
    def amount_formatted(self) -> str:
        currency = currencies[self.currency]

        str_format = "%%d.%%.%dd%%s" % currency.decimals
        return str_format % (int(self.amount / (10 ** currency.decimals)),
                             int(self.amount % (10 ** currency.decimals)), currency.suffix)

    already_accounted = Column(Boolean, default=False, index=True)
    waves_transaction_id = Column(String, nullable=True, default=None)
    # TODO: Add timestamp


class BankWithdrawal(Base, BankWithdrawalExt):
    __tablename__ = 'bank_withdrawal'
    WITHDRAWAL_ID_LENGTH = 32

    def __init__(self, *args, **kwargs):
        self.withdrawal_id = ''.join(random.choice(string.digits + string.ascii_uppercase + string.ascii_lowercase)
                                  for _ in range(self.WITHDRAWAL_ID_LENGTH))
        BankWithdrawalExt.__init__(self, *args, **kwargs)

    def accept(self, transaction: BlockchainTransaction):
        assert(self.accepted is False)
        self.currency = transaction.currency
        self.amount = transaction.amount  # TODO: Withdrawal fee - right now 0%
        self.transaction_id = transaction.transaction_id
        self.address = transaction.address
        self.accepted = True

    address = Column(String, ForeignKey('accounts.address'), index=True)
    withdrawal_id = Column(String, primary_key=True)
    currency = Column(String)  # Asset ID
    amount = Column(BigInteger)
    transaction_id = Column(String, ForeignKey('blockchain_transactions.transaction_id'), nullable=True)
    # TODO: Timestamp to purge old failed withdrawals.
    accepted = Column(Boolean, default=False, index=True)
    executed = Column(Boolean, default=False, index=True)

    # TODO: For now refunds should be manual, I think.

class WACSession(Base):
    __tablename__ = 'wac_sessions'
    SESSION_ID_LENGTH = 32

    def __init__(self, address, asset_id):
        self.address = address
        self.asset_id = asset_id
        self.timeout = int(time.time()) + cfg.session_timeout
        # TODO: Make sure to use a secure source of randomness here
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


class Parameters(Base):
    __tablename__ = 'parameters'

    def __init__(self, key: str, value):
        self.key = key
        self.value = json.dumps(value)

    key = Column(String, primary_key=True)
    value = Column(String)

    @classmethod
    def get(cls, session: Session, key: str, default_value=None):
        param = session.query(cls).get(key)
        if param is None:
            param = Parameters(key, default_value)
            session.add(param)
            session.commit()
            return default_value
        return json.loads(param.value)

    @classmethod
    def set(cls, session: Session, key: str, value):
        param = session.query(cls).get(key)
        if param is None:
            param = Parameters(key, value)
            session.add(param)
        else:
            param.value = json.dumps(value)
        session.commit()
