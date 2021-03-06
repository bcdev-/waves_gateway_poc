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
form = sys.argv[3]

url = "http://127.0.0.1:%d/v1/forms/%s" % (config.port, form)
url += "?Public-Key=%s&Asset-Id=%s&Address=%s&Timestamp=%s" % (pubkey, config.assets[0]["id"], address, str(int(time.time() * 1000)))

print(url)
r = requests.get(url)

#print(json.dumps(r.json(), sort_keys=True,
#                 indent=4, separators=(',', ': ')))
print(r.status_code)
print(r.text.replace("<br/>", "\n").replace("&nbsp;", " "))

