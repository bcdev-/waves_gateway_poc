port = 6771

db_url = "sqlite:///gateway.db"

waves_api_url = "http://127.0.0.1:6869"
waves_api_key = "evik904i5v9mgoupgsnio"

testnet = True

gateway_address = "3N3qmHa1MBo3ZjDYJZbHNezY4RfhtTFxjXG"
gateway_communication_private_key = b'\x88rz\x037{\xfb\xa1\xb3e\\^\xcb\x97\x8d\xa1q\xe0$\xaa\xd7"\xeeI\xff\xf9!Jt~pa'
import curve25519, base58
gateway_communication_public_key = curve25519.public(gateway_communication_private_key)
print("Gateway's public key:", base58.b58encode(gateway_communication_public_key))

default_fee = 100000

currencies = ["6EZjjcsJGT35UGPCDUkcahJD33vXsVeZ6kxsCZ7jzoHw"]

# TODO: Honor confirmations
confirmations = 1

start_from_block = 1730
rescan_blockchain = False

import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

session_timeout = 600  # 10 minutes
