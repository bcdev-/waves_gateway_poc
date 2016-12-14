# Middleware for communicating with the Bank/other blockchains
# Currently it's a dumb simulator

import logging
import json
import os
from src.models import BankDeposit, BankWithdrawal
from src import Session
from .banksim import BankSim


class BankManager:
    def __init__(self):
        self.bank_sim = BankSim()
        self.bank_sim.start()

    def tick(self, session):
        self._handle_withdrawals(session)

    def _handle_withdrawals(self, session: Session):
        for withdrawal in session.query(BankWithdrawal).filter_by(accepted=True, executed=False):
            if withdrawal.type == str(BankWithdrawal.WithdrawalType.bank_transfer):
                withdrawal.executed = True
                session.commit()
                self.bank_sim.send_money(session, withdrawal.bank_account, withdrawal.amount)
                session.commit()
            else:
                raise Exception("Unknown withdrawal type")
