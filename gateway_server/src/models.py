from sqlalchemy import Column, Integer, String
from .api import Base


class Account(Base):
    __tablename__ = 'accounts'

    def __init__(self, address, public_key, deposit_address):
        self.address = address
        self.public_key = public_key
        self.deposit_address = deposit_address

    address = Column(String, primary_key=True, unique=True)
    public_key = Column(String, unique=True)
    deposit_address = Column(String, unique=True)

    def __repr__(self):
        return "<Account(public_key='%s', address='%s')>" % (
                         self.public_key, self.address)

