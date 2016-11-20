import logging
from .api import Api
from .blockchain_manager import BlockchainManager

class Gateway:
    def __init__(self):
        self.api = Api(self)
        self.blockchain_manager = BlockchainManager()

    def start(self):
        logging.basicConfig(level=logging.DEBUG)
        logging.info("Starting GatewayServer version 0.0000")
        self.blockchain_manager.start()
        self.api.start()
