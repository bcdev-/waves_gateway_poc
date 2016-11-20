import logging


class NodeError(Exception):
    def __init__(self):
        logging.error("There was an error regarding your Waves node!")
