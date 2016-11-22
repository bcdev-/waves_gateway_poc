import logging
import datetime
from src import cfg, Base
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Boolean


# Models that extend built-in models and are used to interact with the blockchain

class AccountExt:
    def __init__(self):
        # TODO: Passthrough parameters here please. :-)
        pass

#    address = Column(Integer, ForeignKey('accounts.address'), primary_key=True)
#    kyc_name = Column(String, nullable=True)
#    kyc_surname = Column(String, nullable=True)
#    kyc_address = Column(String, nullable=True)
#    kyc_postcode = Column(String, nullable=True)
#    kyc_city = Column(String, nullable=True)
#    kyc_country = Column(String, nullable=True)
#    kyc_photo = Column(String, nullable=True)
    kyc_completed = Column(Boolean, default=False)


class BankDepositExt:
    def __init__(self):
        print(self.address, self.currency, self.amount)

    # Defined in src.models.BankDeposit
    # address = Column(Integer, ForeignKey('accounts.address'), index=True)
    # Blockchain asset ID
    # currency = Column(String)
    # amount = Column(BigInteger)

    # Your additional fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    #    timestamp = Column(BigInteger)



class BankWithdrawalExt:
    def __init__(self):
        # TODO: Passthrough parameters here please. :-)
        pass

    id = Column(Integer, primary_key=True, autoincrement=True)
#    timestamp = Column(BigInteger)


# Miscellaneous models

