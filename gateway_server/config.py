port = 6771

db_url = "sqlite:///gateway.db"

waves_api_url = "http://127.0.0.1:6869"
waves_api_key = "evik904i5v9mgoupgsnio"

testnet = True

gateway_address = "3N3qmHa1MBo3ZjDYJZbHNezY4RfhtTFxjXG"

default_fee = 100000

currencies = ["SsWUnvrBLJjxsqQedKjG4wtR2UyJGoWL4AU6UqRHhge"]

# TODO: Honor confirmations
confirmations = 1

start_from_block = 1

import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

session_timeout = 600  # 10 minutes
