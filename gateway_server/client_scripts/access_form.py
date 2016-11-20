#!/usr/bin/env python3
import config
import sys
import requests
import src.address
import time
import json
address = sys.argv[1]
pubkey = sys.argv[2]
form = sys.argv[3]

url = "http://127.0.0.1:%d/v1/forms/%s" % (config.port, form)

headers = {"Public-Key": pubkey,
    "Asset-Id": config.assets[0]["id"],
    "Address": address,
    "Timestamp": str(int(time.time() * 1000))}
r = requests.get(url, headers=headers)

#print(json.dumps(r.json(), sort_keys=True,
#                 indent=4, separators=(',', ': ')))
print(r.status_code)
print(r.text)

