from flask import Flask, request, Response
from waitress import serve
import logging
import json
from . import cfg, Session
from functools import wraps
from .node import get_new_deposit_account
from .models import Account
from .address import public_key_to_account
from extensions.forms import list_of_forms

flask = Flask(__name__)


def wac_headers(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        # TODO
        try:
            wac = {}
            wac['public_key'] = request.args['Public-Key']
            wac['asset_id'] = request.args['Asset-Id']
            wac['timestamp'] = int(request.args['Timestamp'])
            assert(request.args['Address'] == public_key_to_account(wac['public_key']))
            wac['address'] = request.args['Address']
        except Exception:
            content = {'message': 'WAC header invalid'}
            return json.dumps(content), 403

        return f(wac, *args, **kwds)
    return wrapper


@flask.route("/")
def index():
    return "GatewayServer v0.0000 :-)"


@flask.route("/v1/details")
def details():
    return Response(json.dumps({
        "description": "This is a super duper BTC Gateway! Please enter <KYC> to continue.",
        "icon": "http://equestriangateway.bcdev.net/icon.png",
        "version": 1,
        "interactive": True
    }), mimetype='application/javascript')


@flask.route("/v1/register", methods=["POST"])
@wac_headers
def register(wac):
    session = Session()
    account = session.query(Account).filter_by(address=wac['address']).first()
    if account is None:
        account = Account(address=wac['address'], public_key=wac['public_key'], deposit_address=get_new_deposit_account())
        session.add(account)
        logging.debug("Registering new account: " + str(account))

    session.commit()

    data = {
        "greetings_form": "greetings",
        "asset_details_message": "This page is directly BELOW the asset info :-)",
        "buttons": [{
            "name": "Deposit",
            "description": "Deposit Equestrian Bits",
            "iframe_form": "deposit",
            # TODO: SendWaves&Currency form
            "main_page": 1
        },
        {
            "name": "Withdraw",
            "description": "Withdraw Equestrian Bits",
            "iframe_form": "withdraw",
            "main_page": 2
        }]
    }

    return json.dumps(data)


@flask.route("/v1/forms/<string:form_name>", methods=["GET"])
@wac_headers
def forms(wac, form_name):
    session = Session()

    account = session.query(Account).filter_by(address=wac['address']).first()
    if account is None:
        return "You are not registered. This should never happen, your wallet is malfunctioning.", 500

    if form_name in list_of_forms:
        return list_of_forms[form_name](wac, session, form_name, account)
    return "Form does not exist", 404


class Api:
    def __init__(self, Gateway):
        pass

    @staticmethod
    def start():
        # flask.run(host='0.0.0.0', port=cfg.port, debug=True)
        serve(flask, host='0.0.0.0', port=cfg.port, threads=1)

