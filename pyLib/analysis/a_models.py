from http import server
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.sql import *
from pyLib.analysis.a_db import a_Base, adb_session


class ASession(a_Base):

    __tablename__ = 'sessions'
    id = Column('session_id', Integer, primary_key=True, nullable=False)
    ip = Column('ip', String(16), nullable=False)
    continent = Column('continent', String, nullable=False, server_default=text(''))
    country = Column('country', String, nullable=False, server_default=text(''))
    city = Column('city', String, nullable=False, server_default=text(''))
    os = Column('os', String, nullable=False, server_default=text(''))
    browser = Column('browser', String, nullable=False, server_default=text(''))
    session = Column('session', String, nullable=False, server_default=text(''))
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


    def _new_page(data):
        new_p = APage(name = data["name"], href = data["href"])
        TRY = 10
        while True:
            isNew = APage._id_by_name(data["name"], data["href"])
            if not isNew == -1:
                return -1
            adb_session.add(new_p)
            try:
                adb_session.commit()
                return APage._id_by_name(data["name"], data["href"])
            except:
                adb_session.rollback()
                if TRY > 0:
                    TRY -= 1
                else:
                    return -2


class Visit(a_Base):

    __tablename__ = 'Visits'

    id = Column('visit_id', Integer, primary_key=True, nullable=False)
    sessid = Column('sess_id', Integer, ForeignKey=("sessions.session_id"), nullable=False)
    pageid = Column('p_id', Integer, ForeignKey=("pages.page_id"), nullable=False)
    created_at = Column('created_at', DateTime, nullable=False, server_default=func.now())


    def _id_lastVis(sid, pid):
        QUERY = select(Visit).where(and_(Visit.sessid == sid, Visit.pageid == pid)).order_by(Visit.id.desc())
        res = adb_session.execute(QUERY).first()
        if res:
            return res[0].id
        return -1


    def _new_visit(sid, pid):
        pageUp = APage._page_by_id(pid)
        newVis = Visit(sessid = sid, pageid = pid)
        TRY = 20
        while True:
            adb_session.add(newVis)
            pageUp.visit = int(pageUp.visit) + 1
            try:
                adb_session.commit()
                return Visit._id_lastVis(sid, pid)
            except:
                adb_session.rollback()
                if TRY > 0:
                    TRY -= 1
                else:
                    return -1
