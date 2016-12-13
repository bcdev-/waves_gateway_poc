from .cfg import currencies
from .node import get_transaction
import json


class Currency:
    def __init__(self, id, name, description, decimals):
        self.id = id
        self.name = name
        self.description = description
        self.decimals = decimals

        d = json.loads(description)

        self.prefix = d['prefix']
        self.suffix = d['suffix']

        # TODO: 1. Check if communication_public_key is the same
        # TODO: 2. Add support for multiple communication keys for multiple currencies - someone might need it


def _read_all_currencies():
    all_items = dict()
    for id in currencies:
        currency = get_transaction(id)
        all_items[id] = Currency(currency['id'], currency['name'], currency['description'], currency['decimals'])
    return all_items

currencies = _read_all_currencies()
