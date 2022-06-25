from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.sql import *
from sqlalchemy.orm import relationship
from app.pyLib.db.datab import Base, db_session
from werkzeug.security import check_password_hash, generate_password_hash


####################################################################################################
####################################################################################################

USERNAME_MAX = 20
HASH_MAX = 120

# USER Object
class User(Base):

    __tablename__ = 'users'

    id = Column('user_id', Integer, primary_key=True, nullable=False)
    username = Column('username', String(USERNAME_MAX), unique=True, nullable=False)
    hash = Column('hash', String(HASH_MAX), nullable=False)
    permission = Column('permission', Integer, nullable=False, server_default=text("0"))
    create_at = Column('created_at', DateTime, server_default=func.now(), nullable=False)
    updated_at = Column('updated_at', DateTime, server_default=func.now(), nullable=False)
    

    # Select USER By USERNAME
    def __USER_by_uname(uname: str):
        QUERY = select(User).where(User.username == uname)
        result = db_session.execute(QUERY).first()
        if result:
            return result[0]
        return -1

    # Select USER By ID
    def __USER_by_id(ID: int):
        QUERY = select(User).where(User.id == ID)
        result = db_session.execute(QUERY).first()
        if result:
            return result[0]
        return -1

    # Check password Hash Validation
    def _validate_password(uname: str, passw: str) -> int:
        result = User.__USER_by_uname(uname)
        if result == -1:
            return result
        if check_password_hash(result.hash, passw):
            return 0, result
        return -2

    # Insert New USER
    def _new_user(uname: str, passw: str, perm: int = 0) -> int:
        TRY = 10
        newUser = User(username = uname, hash = generate_password_hash(passw), permission = perm)
        while True:
            user = User.__USER_by_uname(uname)
            if user != -1:
                return user
            db_session.add(newUser)
            try:
                db_session.commit()
                return User.__USER_by_uname(uname)
            except:
                db_session.rollback()
                print("Wait for connection...")
                if TRY > 0:
                    TRY -= 1
                else:
                    return -1
    

    # Update user USERNAME
    def _update_username(uname: str, passw: str, nuname: str) -> int:
        TRY = 10
        user = User.__USER_by_uname(uname)
        if user == -1:
            return user
        if not check_password_hash(user.hash, passw):
            return -2
        while True:
            if User.__USER_by_uname(nuname) != -1:
                return -3
            try:
                user.username = nuname
                user.updated_at = func.now()
                db_session.commit()
                return user
            except:
                db_session.rollback()
                print("Wait for connection...")
                if TRY > 0:
                    TRY -= 1
                else:
                    return -4
    
    # Update user PASSWORD
    def _update_password(uname: str, passw: str, npassw: str):
        TRY = 10
        user = User.__USER_by_uname(uname)
        if user == -1:
            return user
        if not check_password_hash(user.hash, passw):
            return -2
        newHash = generate_password_hash(npassw)
        while True:
            try:
                user.hash = newHash
                user.updated_at = func.now()
                db_session.commit()
                return user
            except:
                db_session.rollback()
                print("Wait for connection...")
                if TRY > 0:
                    TRY -= 1
                else:
                    return -4

        
####################################################################################################
####################################################################################################


# REFERENCE Object
class HReference(Base):

    __tablename__ = 'hrefs'

    id = Column('href_id', Integer, primary_key=True, nullable=False)
    name = Column('name', String, nullable=False)
    value = Column('value', String, nullable=False)
    href = Column('href', String, nullable=False)
    create_at = Column('created_at', DateTime, server_default=func.now(), nullable=False)
    updated_at = Column('updated_at', DateTime, server_default=func.now(), nullable=False)
    
    def _hrefList(act: str, isAd: int = 0):
        REFS = select(HReference)
        REFS = db_session.execute(REFS).all()
        refs = []
        for r in REFS:
            activ = 'active' if act == r[0].name else ''
            tmpDict = {"name": r[0].name, "value": r[0].value, "href": r[0].href, "active": activ}
            refs.append(tmpDict)
        if isAd:
            activ = 'active' if act == 'admin' else ''
            tmpDict = {"name": 'admin', "value": 'پنل مدیریت', "href": '/admin', "active": activ}
            refs.append(tmpDict)
            tmpDict = {"name": 'logout', "value": 'خروج', "href": '/admin/logout', "active": ''}
            refs.append(tmpDict)
        return refs

    def _newRef(rname: str, rvalue: str, rhref: str):
        QUERY = select(HReference).where(HReference.name == rname)
        print(QUERY)
        result = db_session.execute(QUERY).first()
        if result:
            return result[0]
        newref = HReference(name = rname, value = rvalue, href = rhref)
        TRY = 10
        while True:
            db_session.add(newref)
            try:
                db_session.commit()
                newref = db_session.execute(QUERY).first()
                return newref[0]
            except:
                db_session.rollback()
                if TRY > 0:
                    TRY -= 1
                else:
                    return -2

# REFERENCES CATEGORY
class RefCat(Base):

    __tablename__ = 'refcats'

    id = Column('refcat_id', Integer, primary_key=True, nullable=False)
    name = Column('name', String, unique=True, nullable=False)
    href_id = Column('href_id', Integer, ForeignKey('hrefs.href_id'), nullable=False)
    hrefs = relationship('HReference', backref='hrefs')

