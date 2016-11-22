#!/usr/bin/env python3
import sys
sys.path.append("..")
import config
import requests
import src.address
import time
import json
address = sys.argv[1]
pubkey = sys.argv[2]

url = "http://127.0.0.1:%d/v1/register" % config.port

headers = {"Public-Key": pubkey,
    "Asset-Id": config.assets[0]["id"],
    "Address": address,
    "Timestamp": str(int(time.time() * 1000))}
r = requests.post(url, headers=headers)

print(json.dumps(r.json(), sort_keys=True,
                 indent=4, separators=(',', ': ')))

