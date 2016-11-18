from sqlalchemy import Column, Integer, String
from .api import Base

class Account(Base):
    __tablename__ = 'accounts'

    public_key = Column(String, primary_key=True)
    address = Column(String)
    deposit_address = Column(String)
    deposit_public_key = Column(String)

    def __repr__(self):
        return "<Account(public_key='%s', address='%s')>" % (
                         self.public_key, self.address)

