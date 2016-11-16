from flask import Flask, request, Response
from waitress import serve
import logging
import json
from . import config

flask = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(config.db_url, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
Base.metadata.create_all(bind=engine)

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
def register():
    return json.dumps("TODO: Register call")

@flask.route("/v1/forms", methods=["GET"])
def forms():
    return "LOLZIES"

class Api:
    def __init__(self, Gateway):
        pass

    def start(self):
#        flask.run(host='0.0.0.0', port=config.port, debug=True)
        serve(flask, host='0.0.0.0', port=config.port, threads=1)

