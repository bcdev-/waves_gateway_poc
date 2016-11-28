# Middleware for communicating with the Bank/other blockchains
# Currently it's a dumb simulator

import logging
import json
import os
from src.models import BankDeposit, BankWithdrawal
from .banksim import BankSim


class BankManager:
    def __init__(self):
        self.bank_sim = BankSim()
        self.bank_sim.start()

    def tick(self, session):
        pass
