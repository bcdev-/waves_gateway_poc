import multiprocessing
from flask import Flask, request, Response
from waitress import serve
from src.models import BankDeposit, BankWithdrawal, Account
from .banking_models import BankSimBalances
from src import Session
from src.currency import currencies

flask = Flask(__name__)


@flask.route("/", methods=["GET", "POST"])
def index():
    session = Session()
    if "account" in request.form and "amount" in request.form:
        iban = request.form["account"]
        amount = int(float(request.form["amount"]) * (10**list(currencies.values())[0].decimals))

        account = session.query(Account).filter_by(iban=iban).first()
        if account is None:
            return "There is no account with IBAN %s" % (iban)

        deposit = BankDeposit(account.address, list(currencies.values())[0].id, amount)
        session.add(deposit)
        session.commit()
        return """Your deposit to %s for %d.%.2d USD was made""" % (iban, amount / (10.**list(currencies.values())[0].decimals),
                                                                    amount % (10.**list(currencies.values())[0].decimals))
    session.commit()
    msg = """Welcome to the Bank simulator!<br/>Make a deposit:
    <form method='POST' action='/'>
    Account [IBAN]:<input name='account'/><br/>
    Amount [Bits]:<input name='amount'/><br/>
    <input type='submit'/></form><br/>
    <b>Account balances:</b><br/>"""

    for balance in session.query(BankSimBalances).all():
        msg += "%s - %d.%.2d<br/>" % (balance.bank_account, balance.balance / 100, balance.balance % 100)

    return msg


class BankSim(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)

    def send_money(self, session: Session, account: str, amount: int):
        acc = session.query(BankSimBalances).filter_by(bank_account=account).first()
        if acc is None:
            acc = BankSimBalances(account, amount)
            session.add(acc)
        else:
            acc.balance += amount

    def run(self):
        # flask.run(host='0.0.0.0', port=7777, debug=True)
        serve(flask, host='0.0.0.0', port=7777, threads=1)
