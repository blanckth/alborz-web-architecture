from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


A_DATABASE = 'sqlite:///db/analysis.db'
a_engine = create_engine(A_DATABASE)
adb_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=a_engine))
a_Base = declarative_base()
a_Base.query = adb_session.query_property()

import pyLib.analysis.a_models

a_Base.metadata.create_all(bind=a_engine)


