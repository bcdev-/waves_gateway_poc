port = 6771

db_url = "sqlite:///gateway.db"

waves_api_url = "http://127.0.0.1:6869"
waves_api_key = "evik904i5v9mgoupgsnio"

testnet = True

gateway_address = "3N3qmHa1MBo3ZjDYJZbHNezY4RfhtTFxjXG"

default_fee = 100000

assets = [
    {
        "id": "BEbJsWWmyGtUuNtFckRFkmHq4ivw2EEYZJw5q74WUiBm",
        "name": "Equestrian Bit",
        "digits": 2
    }]

# TODO: Honor confirmations
confirmations = 1

start_from_block = 2560

import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

