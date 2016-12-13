import logging
import datetime
import string
import random
from src import cfg, Base
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Boolean
from enum import Enum


# Models that extend built-in models and are used to interact with the blockchain

class AccountExt:
    def __init__(self):
        # TODO: Passthrough parameters here please. :-)
        self.iban = self._create_mock_iban_account()
        pass

    def _create_mock_iban_account(self) -> str:
        return "EQ" + ''.join(random.choice(string.digits) for _ in range(15))

    iban = Column(String, index=True)
    kyc_name = Column(String, nullable=True, default=None)
    kyc_completed = Column(Boolean, default=False)


class BankDepositExt:
    def __init__(self):
        print(self.address, self.currency, self.amount)

    id = Column(Integer, primary_key=True, autoincrement=True)


class BankWithdrawalExt:
    def __init__(self, bank_account):
        self.bank_account = bank_account
        self.type = str(self.WithdrawalType.bank_transfer)

    class WithdrawalType(Enum):
        bank_transfer = "bank_transfer"

    # TODO: Consider using a native SQLAlchemy Enum here
    type = Column(String)
    bank_account = Column(String)


# Miscellaneous models

