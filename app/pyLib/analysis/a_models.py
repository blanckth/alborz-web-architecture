from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.sql import *
from sqlalchemy.orm import relationship
from app.pyLib.analysis.a_db import a_Base, adb_session

class ASession(a_Base):

    __tablename__ = 'sessions'
    id = Column('session_id', Integer, primary_key=True, nullable=False)
    ip = Column('ip', String, nullable=False)
    continent = Column('continent', String, nullable=False, server_default=text('continent'))
    country = Column('country', String, nullable=False, server_default=text('country'))
    city = Column('city', String, nullable=False, server_default=text('city'))
    os = Column('os', String, nullable=False, server_default=text('os'))
    browser = Column('browser', String, nullable=False, server_default=text('browser'))
    session = Column('session', String, nullable=False, server_default=text('session'))
    created_at = Column('created_at', DateTime, nullable=False, server_default=func.now())

    def _id_by_ip(sip):
        QUERY = select(ASession).where(ASession.ip == sip)
        sess = adb_session.execute(QUERY).first()
        if sess:
            return sess[0].id
        return -1

    def _session_by_id(sid):
        QUERY = select(ASession).where(ASession.id == sid)
        sess = adb_session.execute(QUERY).first()
        if sess:
            return sess[0]
        return -1

    def _new_session(data):
        new_sess = ASession(ip = data["ip"], continent = data["continent"], country = data["country"], city = data["city"], os = data["os"], browser = data["browser"], session = data["session"])
        TRY = 10
        while True:
            isNew = ASession._id_by_ip(data["ip"])
            if not isNew == -1:
                return -1
            adb_session.add(new_sess)
            try:
                adb_session.commit()
                return ASession._id_by_ip(data["ip"])
            except:
                adb_session.rollback()
                if TRY > 0:
                    TRY -= 1
                else:
                    return -2

class APage(a_Base):

    __tablename__ = 'pages'

    id = Column('page_id', Integer, primary_key=True, nullable=False)
    name = Column('name', String, nullable=False)
    href = Column('href', String, nullable=False)
    visit = Column('visit', Integer, nullable=False, server_default=text('0'))
    visit_h = Column('visit_h', Integer, nullable=False, server_default=text('0'))
    visit_d = Column('visit_d', Integer, nullable=False, server_default=text('0'))
    visit_m = Column('visit_m', Integer, nullable=False, server_default=text('0'))
    visit_y = Column('visit_y', Integer, nullable=False, server_default=text('0'))
    created_at = Column('created_at', DateTime, nullable=False, server_default=func.now())
    updated_at = Column('updated_at', DateTime, nullable=False, server_default=func.now())

    def _id_by_name(pname, phref):
        QUERY = select(APage).where(and_(APage.name == pname, APage.href == phref))
        page = adb_session.execute(QUERY).first()
        if page:
            return page[0].id
        return -1


    def _page_by_id(pid):
        QUERY = select(APage).where(APage.id == pid)
        page = adb_session.execute(QUERY).first()
        if page:
            return page[0]
        return -1

    def _page_by_name(pname, phref):
        QUERY = select(APage).where(and_(APage.name == pname, APage.href == phref))
        page = adb_session.execute(QUERY).first()
        if page:
            return page[0]
        return -1

    def _new_page(pname, phref):
        new_p = APage(name = pname, href = phref)
        TRY = 10
        while True:
            isNew = APage._page_by_name(pname, phref)
            if not isNew == -1:
                return isNew
            adb_session.add(new_p)
            try:
                adb_session.commit()
                return APage._page_by_name(pname, phref)
            except:
                adb_session.rollback()
                if TRY > 0:
                    TRY -= 1
                else:
                    return -1


class Visit(a_Base):

    __tablename__ = 'visits'

    id = Column('visit_id', Integer, primary_key=True, nullable=False)
    sessid = Column('sess_id', Integer, ForeignKey("sessions.session_id"), nullable=False)
    pageid = Column('p_id', Integer, ForeignKey("pages.page_id"), nullable=False)
    created_at = Column('created_at', DateTime, nullable=False, server_default=func.now())
    sessions = relationship("ASession", backref="sessions")
    pages = relationship("APage", backref="pages")


    def _id_lastVis(sid, pid):
        QUERY = select(Visit).where(and_(Visit.sessid == sid, Visit.pageid == pid)).order_by(Visit.id.desc())
        res = adb_session.execute(QUERY).first()
        if res:
            return res[0].id
        return -1


    def _new_visit(sid, pname, phref):
        pageUp = APage._new_page(pname, phref)
        if pageUp == -1:
            return -1
        newVis = Visit(sessid = sid, pageid = pageUp.id)
        curVis = int(pageUp.visit)
        upVisit = curVis + 1
        TRY = 20
        while True:
            adb_session.add(newVis)
            pageUp.visit = upVisit
            try:
                adb_session.commit()
                return upVisit
            except:
                adb_session.rollback()
                if TRY > 0:
                    TRY -= 1
                else:
                    return -2
