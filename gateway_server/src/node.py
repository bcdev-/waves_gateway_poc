from requests import get, post
from .cfg import waves_api_url, waves_api_key
from unittest import TestCase
from .exceptions import NodeError


def get_new_deposit_account():
    try:
        url = waves_api_url + "/addresses"
        headers = {'api_key': waves_api_key}
        r = post(url, headers=headers)
        return r.json()['address']
    except Exception:
        raise NodeError()


def get_transactions_for_account(account):
    try:
        url = waves_api_url + "/transactions/address/%s/limit/1000" % account
        headers = {'api_key': waves_api_key}
        r = get(url, headers=headers)
        return r.json()[0]
    except Exception:
        raise NodeError()


def get_current_height():
    try:
        url = waves_api_url + "/blocks/height"
        r = get(url)
        return r.json()["height"]
    except Exception:
        raise NodeError()


def get_block(height):
    try:
        url = waves_api_url + "/blocks/at/%d" % height
        r = get(url)
        return r.json()
    except Exception:
        raise NodeError()


def get_transactions_for_block(height):
    return get_block(height)["transactions"]


class TestNode(TestCase):
    def test_new_deposit_account(self):
        a1 = get_new_deposit_account()
        a2 = get_new_deposit_account()
        a3 = get_new_deposit_account()
        self.assertNotEqual(a1, a2)
        self.assertNotEqual(a2, a3)
