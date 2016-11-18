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

class Test(TestCase):
    def test_omg(self):
        a1 = get_new_deposit_account()
        a2 = get_new_deposit_account()
        a3 = get_new_deposit_account()
        self.assertNotEqual(a1, a2)
        self.assertNotEqual(a2, a3)
