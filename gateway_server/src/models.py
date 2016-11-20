import logging
from . import cfg
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from .api import Base


class Account(Base):
    __tablename__ = 'accounts'

    def __init__(self, address, public_key, deposit_address):
        self.address = address
        self.public_key = public_key
        self.deposit_address = deposit_address

    address = Column(String, unique=True, primary_key=True)
    public_key = Column(String, unique=True)
    deposit_address = Column(String, unique=True)

    def __repr__(self):
        return "<Account(public_key='%s', address='%s')>" % (
                         self.public_key, self.address)


# TODO: Deposit history

class Balance(Base):
    __tablename__ = 'balances'

    def __init__(self, address, currency):
        self.address = address
        self.currency = currency
        self.balance = 0

    address = Column(Integer, ForeignKey('accounts.address'), primary_key=True)
    currency = Column(String, primary_key=True)
    balance = Column(BigInteger)

    @staticmethod
    def get_all_balances(session, account):
        balances = Balance.query.filter_by(address=account.address).all()
        final_balances = []
        missing_currencies = set([id["id"] for id in cfg.assets])
        for balance in balances:
            if balance.currency not in missing_currencies:
                logging.warning("Currency %s is not defined in configuration!")
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
