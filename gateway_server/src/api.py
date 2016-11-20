from flask import Flask, request, Response
from waitress import serve
import logging
import json
from . import cfg
from functools import wraps
from .node import get_new_deposit_account

flask = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .address import public_key_to_account

engine = create_engine(cfg.db_url, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
Base.metadata.create_all(bind=engine)

from .models import Account, Balance
Base.metadata.create_all(bind=engine)


def wac_headers(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        # TODO
        try:
            wac = {}
            wac['public_key'] = request.headers['Public-Key']
            wac['asset_id'] = request.headers['Asset-Id']
            wac['timestamp'] = int(request.headers['Timestamp'])
            assert(request.headers['Address'] == public_key_to_account(wac['public_key']))
            wac['address'] = request.headers['Address']
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
    account = Account.query.filter_by(address=wac['address']).first()
    if account == None:
        account = Account(address=wac['address'], public_key=wac['public_key'], deposit_address=get_new_deposit_account())
        db_session.add(account)
        db_session.commit()
        logging.debug("Registering new account: " + str(account))

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
    account = Account.query.filter_by(address=wac['address']).first()
    if account is None:
        return "You are not registered. This should never happen, your wallet is malfunctioning.", 404
    if form_name == "greetings":
        s = "Greetings! Your deposit address: %s\nSupported currencies:\n\t%s\n" % (account.deposit_address, "\n\t".join([c["name"] + " - " + c["id"] for c in cfg.assets]))
        s += "Your Balances: \n\t%s\n" % "\n\t".join([str(b.currency) + " = " + str(b.balance) for b in Balance.get_all_balances(db_session, account)])
        return s
    return "Does not exist", 404

class Api:
    def __init__(self, Gateway):
        pass

    @staticmethod
    def start():
        # flask.run(host='0.0.0.0', port=config.port, debug=True)
        serve(flask, host='0.0.0.0', port=cfg.port, threads=1)

