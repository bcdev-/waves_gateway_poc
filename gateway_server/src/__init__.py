from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from . import cfg

engine = create_engine(cfg.db_url, convert_unicode=True)
Session = sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine)
Base = declarative_base()
#Base.query = Session.query_property()
from . import models
Base.metadata.create_all(bind=engine)
