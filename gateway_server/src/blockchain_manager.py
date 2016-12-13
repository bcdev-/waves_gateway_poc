import multiprocessing
import logging
import time
from src.node import send_currency
from . import Session, node, cfg
from .models import Account, Balance, BlockchainTransaction, BankDeposit, Parameters
from .transaction import TransactionTypes
from extensions.bank_manager import BankManager


# BlockchainManager is single-threaded for now
# If we need more threads, we'll add them
class BlockchainManager(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.bank_manager = BankManager()

    def run(self):
        logging.info("Blockchain manager started")

        if cfg.rescan_blockchain:
            session = Session()
            Parameters.set(session, "current_block", cfg.start_from_block)
            session.commit()

        # TODO: Deal with double-spent transactions
        # TODO: Try&catch
        while True:
            session = Session()
            # TODO: This is overly simplistic. What if there is an orphan?
            current_block = Parameters.get(session, "current_block", cfg.start_from_block)
            if current_block < cfg.start_from_block:
                current_block = cfg.start_from_block
                Parameters.set(session, "current_block", current_block)

            while current_block <= node.get_current_height():
                logging.info("Scanning block %d" % current_block)
                self._scan_block(session, current_block)
                current_block += 1
                Parameters.set(session, "current_block", current_block)
            self._update_balances(session)
            self.bank_manager.tick(session)

            # I'm assuming that we're withdrawing to the wallet immediately for now
            # self._account_banking_deposits(session)
            self._withdraw_banking_deposits(session)

            session.commit()
            session.flush()
            time.sleep(1)

    @staticmethod
    def _withdraw_banking_deposits(session: Session):
        # Bank deposit can either be "accounted" or it can be withdrawn to the wallet
        # TODO: Add additional if's for KYC and such things
        new_deposits = session.query(BankDeposit).filter_by(already_accounted=False, waves_transaction_id=None)
        for deposit in new_deposits:
            # TODO: Please rewrite this... If someone runs two BlockchainManagers at once everything will go to...
            # TODO: Check if such account exists and is not banned for example
            # TODO: Treat empty waves_transaction_id as a failure
            deposit.waves_transaction_id = ""
            session.commit()
            session.flush()
            deposit.waves_transaction_id = send_currency(deposit.currency, deposit.address, deposit.amount)
            session.commit()
            session.flush()
            # Send 0.1 Waves for transaction fees if the client has less than 0.01
            if node.get_waves_balance(deposit.address) < 1000000:
                send_currency(None, deposit.address, 10000000)

    @staticmethod
    def _update_balances(session):
        new_transactions = session.query(BlockchainTransaction).filter_by(already_accounted=False)
        for transaction in new_transactions:
            # TODO: Please rewrite this... If someone runs two BlockchainManagers at once everything will go to...
            balance = session.query(Balance).filter_by(address=transaction.address, currency=transaction.currency).first()
            balance.balance += transaction.amount
            transaction.already_accounted = True

    @staticmethod
    def _account_banking_deposits(session):
        # Bank deposit can either be "accounted" or it can be withdrawn to the wallet
        new_deposits = session.query(BankDeposit).filter_by(already_accounted=False, waves_transaction_id=None)
        for deposit in new_deposits:
            # TODO: Please rewrite this... If someone runs two BlockchainManagers at once everything will go to...
            balance = session.query(Balance).filter_by(address=deposit.address, currency=deposit.currency).first()
            balance.balance += deposit.amount
            deposit.already_accounted = True

    @staticmethod
    def _scan_block(session, height):
        transactions = node.get_transactions_for_block(height)
        for tx in transactions:
            if tx["type"] == TransactionTypes.transfer_asset:
                account = session.query(Account).filter_by(deposit_address=tx["recipient"]).first()
                if account and session.query(BlockchainTransaction).get(tx["id"]) is None:
                    logging.info("♡ A new deposit transaction received. - %s" % tx["id"])
                    logging.info("\tFrom %s" % account.address)
                    logging.info("\tAsset %s" % tx["assetId"])
                    logging.info("\tAmount %d" % tx["amount"])
                    # TODO: Check if currency is defined
                    blockchain_transaction = BlockchainTransaction(tx["id"], account.address, tx["type"], tx["timestamp"], tx["assetId"], tx["amount"])
                    session.add(blockchain_transaction)
