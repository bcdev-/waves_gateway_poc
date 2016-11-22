from src.models import Account, Balance, BlockchainTransaction
from src import cfg


def greetings_form(wac, session, form_name, account):
    s = "Greetings! Your deposit address: %s\nSupported currencies:\n\t%s\n" % (
    account.deposit_address, "\n\t".join([c["name"] + " - " + c["id"] for c in cfg.assets]))
    s += "Your Balances: \n\t%s\n" % "\n\t".join(
        [str(b.currency) + " = " + str(b.balance) for b in Balance.get_all_balances(session, account)])
    s += "Your past deposits/withdrawals: \n\t%s\n" % "\n\t".join(
        [str(b.timestamp_readable) + " " + str(b.currency) + " -> " + str(b.amount) for b in
         BlockchainTransaction.get_all_transactions(session, account)])
    return s

list_of_forms = {"greetings": greetings_form}
