from sqlalchemy.orm.session import Session
from flask import request

from src.models import Account, Balance, BlockchainTransaction, BankDeposit, BankWithdrawal
from src import cfg
from src.node import get_currency_balance


def kyc_incomplete(wac):
    s = "Greetings! Welcome to out bank!<br/>"
    s += "Fill in KYC:<form action='/v1/forms/kyc'>"
    s += "Your name: <input name='name'/><br/><br/>"
    s += """Your country:
    <select name="country">
      <option value="usa">United States</option>
      <option value="iran">Iran</option>
    </select>
    """
    s += "<input type='submit'/>"
    s += "<input type='hidden' name='Session-Id' value='%s'/>" % wac['session_id']
    s += "</form>"
    return s


# TODO: Declare WAC as a class
def details_form(wac, session: Session, form_name: str, account: Account):
    if account.kyc_completed is False:
        s = kyc_incomplete(wac)

    else:
        s = "Welcome %s!<br/><br/>" % account.kyc_name
        s += "Account verification: <font color='#0a0'>OK</font>. Withdrawal limit per day: $2000/$2000.<br/><br/>"

        currency = wac['currency']
        format = "%%d.%%.%dd%%s" % currency.decimals
        amount = get_currency_balance(account.address, currency.id)
        balance = format % (int(amount / (10 ** currency.decimals)),
                         int(amount % (10 ** currency.decimals)), currency.suffix)

        s += "<a href='/v1/forms/change_your_data?Session-Id=%s'>Change your data</a><br/><br/>" % wac['session_id']

        s += "Your current balance: %s <a href='/v1/forms/deposit?Session-Id=%s'>Deposit funds</a> | <a href='/v1/forms/withdraw?Session-Id=%s'>Withdraw funds</a> <br/><br/>" % (balance, wac['session_id'], wac['session_id'])
        s += "<a href='/v1/forms/deposit_withdrawal_history?Session-Id=%s'>Deposit/withdrawal history</a><br/><br/>" % wac['session_id']
        s += "<a href='/v1/forms/support?Session-Id=%s'>Contact support</a><br/><br/>" % wac['session_id']

    s += "<button onclick=\"window.top.postMessage(['gateway_close_form'], '*');\">Close</button>"
    return s


def kyc(wac, session: Session, form_name: str, account: Account):
    if request.args['country'] == 'iran':
        s = "Unfortunately, due to government regulation, we're currently unable to serve customers from Iran.<br/><br/>"
        s += "<button onclick=\"window.top.postMessage(['gateway_close_form'], '*');\">Close</button>"
        return s
    account.kyc_name = request.args['name']
    account.kyc_completed = True
    session.commit()
    return "KYC completed. Your account number is: %s" % account.iban


def withdraw(wac, session: Session, form_name: str, account: Account):
    if account.kyc_completed is False:
        s = kyc_incomplete(wac)
    elif 'bank_account' in request.args:
        # TODO: Obviously validate the account number.
        withdrawal = BankWithdrawal(request.args['bank_account'])
        session.add(withdrawal)
        session.commit()
        attachment = "%s" % withdrawal.withdrawal_id
        s = """
        Welcome %s!<br/>
        You are about to withdraw your money to an account number %s.<br/>
        Money transfer can take up to 3 days depending on the weather and star alignment.</br>
        <input type='submit' value='Continue withdrawal' onclick="window.top.postMessage(['transfer', '%s', 'You are about to withdraw money to %s.\\nThis is not functional yet, but it will be in the future. :-)\\nAttachment for the withdrawal: %s\\n', '%s'], '*');"/><br/><br/><br/>
        """ % (account.kyc_name, request.args['bank_account'], account.deposit_address, request.args['bank_account'], attachment, attachment)
    else:
        s = """
        Welcome %s!<br/>
        <b>Withdraw using a bank account</b>
        Please enter your account number:
        <form action='/v1/forms/withdraw'>
            <input type='text' name='bank_account'/>
            <input type='submit' value='Withdraw to a bank account'/>
            <input type='hidden' name='Session-Id' value='%s'/>
        </form><br/><br/>""" % (account.kyc_name, wac['session_id'])
        s += """
        <b>Withdraw to PayPal</b>
        To withdraw please enter your PayPal account:
        <form action='/v1/forms/withdraw'>
            <input type='text' name='paypal_account'/>
            <input type='submit' value='Withdraw to PayPal'/>
            <input type='hidden' name='Session-Id' value='%s' enabled=false/>
        </form>""" % wac['session_id']

    s += "<button onclick=\"window.top.postMessage(['gateway_close_form'], '*');\">Cancel</button>"
    return s


def deposit_withdrawal_history(wac, session: Session, form_name: str, account: Account):
    s = "Your past deposits/withdrawals: <br/>\t%s<br/>" % "<br/>\t".join(
        [str(b.timestamp_readable) + " " + str(b.currency) + " -> " + str(b.amount) for b in
         BlockchainTransaction.get_all_transactions(session, account)])

    s += "Your bank deposits: <br/>\t%s<br/><br/>'" % "<br/>\t".join(
        [str(d.currency_name) + " -> " + str(d.amount_formatted) + (
        " <font size='1'>txid: %s</font>" % str(d.waves_transaction_id)) for d in BankDeposit.get_all(session, account)]
    )

    s += "<button onclick=\"window.top.postMessage(['gateway_close_form'], '*');\">Close</button>"
    return s


def deposit(wac, session: Session, form_name: str, account: Account):
    s = "Ways to deposit money:<br/><br/>"
    s += "<b>International money transfer.</b><br/>Your personal deposit bank account: %s<br/>" % account.iban
    s += "Your deposit will be credited on the next workday.<br/><br/>"
    s += "<b>PayPal</b><br/>I'm not familiar with how PayPal works, but it can be integrated, why not.<br/><br/>"
    s += "<b>Credit card</b><br/>I don't think that Credit Card is a good idea, but... :-)<br/><br/>"

    s += "<button onclick=\"window.top.postMessage(['gateway_close_form'], '*');\">Close</button>"
    return s


def change_your_data(wac, session: Session, form_name: str, account: Account):
    s = "<b>You are about to change your data.</b><br/>"
    s += "Fill in KYC:<br/><form action='/v1/forms/kyc'>"
    s += "Your name: <input name='name' value='%s'/><br/><br/>" % account.kyc_name
    s += """Your country:
    <select name="country">
      <option value="usa">United States</option>
      <option value="iran">Iran</option>
    </select><br/><br/>
    """
    s += "<input type='submit'/>"
    s += "<input type='hidden' name='Session-Id' value='%s'/>" % wac['session_id']
    s += "</form><br/><br/>"

    s += "<button onclick=\"window.top.postMessage(['gateway_close_form'], '*');\">Cancel</button>"
    return s


list_of_forms = {"details": details_form, "kyc": kyc, "withdraw": withdraw, "deposit_withdrawal_history": deposit_withdrawal_history,
                 "deposit": deposit, "change_your_data": change_your_data}
