#!/usr/bin/env python3
import config
import requests

def get_new_account():
    url = config.waves_api_url + "/addresses"
    headers = {'api_key': config.waves_api_key}
    r = requests.post(url, headers=headers)
    return r.json()['address'] + " " + r.json()['publicKey']

print(get_new_account())

