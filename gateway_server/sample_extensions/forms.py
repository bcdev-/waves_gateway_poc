from sqlalchemy.orm.session import Session
from flask import request

from src.models import Account, Balance, BlockchainTransaction, BankDeposit
from src import cfg


# TODO: Declare WAC as a class
def greetings_form(wac, session: Session, form_name: str, account: Account):
    if account.kyc_completed is False:
        s = "Greetings! Welcome to out bank!<br/>"
        s += "Fill in KYC:<form action='/v1/forms/kyc'>"
        s += "Your name: <input name='name'/>"
        s += "<input type='submit'/>"
        s += "<input type='hidden' name='Session-Id' value='%s'/>" % wac['session_id']
        s += "</form>"

    else:
        s = "Welcome %s!\n" % account.kyc_name
        s += " Your deposit address: %s\nSupported currencies:\n\t%s\n" % (
            account.deposit_address, "\n\t".join([c["name"] + " - " + c["id"] for c in cfg.assets]))
        s += "Your internal balances: \n\t%s\n" % "\n\t".join(
            [str(b.currency) + " = " + str(b.balance) for b in Balance.get_all_balances(session, account)])
        s += "Your past deposits/withdrawals: \n\t%s\n" % "\n\t".join(
            [str(b.timestamp_readable) + " " + str(b.currency) + " -> " + str(b.amount) for b in
             BlockchainTransaction.get_all_transactions(session, account)])
        s += "Your bank deposits: \n\t%s\n\n'" % "\n\t".join(
            [str(d.currency) + " -> " + str(d.amount) + " - txid: " + str(d.waves_transaction_id) for d in BankDeposit.get_all(session, account)]
        )
        s += "Your bank deposit account: %s\n\n" % account.iban

    return s.replace("\n", "<br/>").replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")


def kyc(wac, session: Session, form_name: str, account: Account):
    account.kyc_name = request.args['name']
    account.kyc_completed = True
    session.commit()
    return "KYC completed. Your account number is: %s" % account.iban

list_of_forms = {"greetings": greetings_form, "kyc": kyc}
