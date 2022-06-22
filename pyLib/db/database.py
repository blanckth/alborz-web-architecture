from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


DATABASE = 'sqlite:///db/app.db'
engine = create_engine(DATABASE)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

import pyLib.db.models
Base.metadata.create_all(bind=engine)


