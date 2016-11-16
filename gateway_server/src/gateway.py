import logging
from .api import Api

class Gateway:
    def __init__(self):
        self.api = Api(self)

    def start(self):
        logging.basicConfig(level=logging.DEBUG)
        logging.info("Starting GatewayServer version 0.0000")
        self.api.start()
#        while True:

