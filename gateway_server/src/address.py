from pyblake2 import blake2b
from sha3 import sha3_256
from base58 import b58decode, b58encode
from unittest import TestCase
from . import cfg


base58_public_key_max_length = 50


class BlockchainParameters:
    def __init__(self, testnet):
        self.testnet = testnet
        self.AddressVersion = b'\x01'
        self.ChainId = b'T' if testnet else b'W'
        self.HashLength = 20
        self.ChecksumLength = 4


def public_key_to_account(public_key, params=BlockchainParameters(testnet=cfg.testnet)):
    def blake2b256_keccak256(data):
        b = blake2b(digest_size=32)
        b.update(data)
        return sha3_256(b.digest()).digest()

    assert(len(public_key) <= base58_public_key_max_length)
    public_key = b58decode(public_key)
    public_key_hash = blake2b256_keccak256(public_key)[:params.HashLength]
    without_checksum = params.AddressVersion + params.ChainId + public_key_hash
    return b58encode(without_checksum + blake2b256_keccak256(without_checksum)[:params.ChecksumLength])


# TODO: Move to individual files
class TestSolver(TestCase):
    def test_public_key_to_account(self):
        self.assertEqual(public_key_to_account("FkoFqtAeibv2E6Y86ZDRfAkZz61LwUMjLAP2gmS1j7xe",
                                               BlockchainParameters(True)), "3Mv61qe6egMSjRDZiiuvJDnf3Q1qW9tTZDB")
        self.assertEqual(public_key_to_account("FZZi4z9TVmev2zh6GyxLQWsieXDaeGthzWhgrQYcv6Ci",
                                               BlockchainParameters(False)), "3PAtGGSLnHJ3wuK8jWPvAA487pKamvQHyQw")

