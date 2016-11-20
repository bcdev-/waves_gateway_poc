import multiprocessing
import logging
import time
from . import Session, node, cfg
from .models import Account, BlockchainTransaction
from .transaction import TransactionTypes


# BlockchainManager is single-threaded for now
# If we need more threads, we'll add them
class BlockchainManager(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.current_block = cfg.start_from_block

    def run(self):
        logging.info("Blockchain manager started")

        # TODO: Deal with double-spent transactions
        # TODO: Try&catch
        while True:
            session = Session()
            while self.current_block < node.get_current_height():
                logging.info("Scanning block %d" % self.current_block)
                self._scan_block(session, self.current_block)
                self.current_block += 1
            session.commit()
            time.sleep(1)

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

        """
        all_accounts = session.query(Account).all()
        for account in all_accounts:
            print(account.deposit_address)
            transactions = node.get_transactions_for_account(account.deposit_address)
            for tx in transactions:
                print(tx)
        """