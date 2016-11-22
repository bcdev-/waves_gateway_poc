# Middleware for communicating with the Bank/other blockchains
# Currently it's a dumb simulator

import logging
import json
import os
from src.models import BankDeposit, BankWithdrawal


class BankManager:
    def __init__(self):
        pass

    def tick(self, session):
        logging.debug("Bank manager running...")
        try:
            file = open("/var/run/shm/deposit.txt").read()
            os.unlink("/var/run/shm/deposit.txt")
            deposit = json.loads(file)
            deposit = BankDeposit("address", "currency", 1000000)
            session.add(deposit)
#            session.query()
        except FileNotFoundError: pass
