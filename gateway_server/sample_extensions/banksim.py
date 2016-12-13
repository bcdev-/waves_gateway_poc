import multiprocessing
from flask import Flask, request, Response
from waitress import serve
from src.models import BankDeposit, BankWithdrawal, Account
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
    return """Welcome to the Bank simulator!<br/>Make a deposit:
    <form method='POST' action='/'>
    Account [IBAN]:<input name='account'/><br/>
    Amount [Bits]:<input name='amount'/><br/>
    <input type='submit'/></form>"""


class BankSim(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)

    def run(self):
        # flask.run(host='0.0.0.0', port=7777, debug=True)
        serve(flask, host='0.0.0.0', port=7777, threads=1)
