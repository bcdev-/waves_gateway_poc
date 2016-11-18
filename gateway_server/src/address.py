from pyblake2 import blake2b
from sha3 import sha3_256
from base58 import b58decode, b58encode

class WavesTestnet:
    testnet = True
    AddressVersion = b'\x01'
    ChainId = b'T' if testnet else b'W'
    HashLength = 20
    ChecksumLength = 4

def publicKeyToAccount(publicKey, params=WavesTestnet):
    def blake2b256_keccak256(data):
        b = blake2b(digest_size=32)
        b.update(data)
        return sha3_256(b.digest()).digest()

    publicKey = b58decode(publicKey)
    publicKeyHash = blake2b256_keccak256(publicKey)[:params.HashLength]
    withoutChecksum = params.AddressVersion + params.ChainId + publicKeyHash
    return b58encode(withoutChecksum + blake2b256_keccak256(withoutChecksum)[:params.ChecksumLength])

print(publicKeyToAccount("FkoFqtAeibv2E6Y86ZDRfAkZz61LwUMjLAP2gmS1j7xe"))

