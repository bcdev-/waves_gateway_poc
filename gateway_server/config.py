port = 6771

db_url = "sqlite:///gateway.db"

waves_api_url = "http://127.0.0.1:6869"
waves_api_key = "evik904i5v9mgoupgsnio"

testnet = True

gateway_address = "3N3qmHa1MBo3ZjDYJZbHNezY4RfhtTFxjXG"

assets = [
    {
        "id": "9882aTipAmkHHQcva6m99ViAELjE82p7C1F2suwXtq2N",
        "name": "Equestrian Bit"
    }]

confirmations = 1

start_from_block = 2980

import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
