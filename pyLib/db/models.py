from sqlalchemy import BLOB, Column, Integer, String, DateTime
from sqlalchemy.sql import *
from pyLib.db.database import Base, db_session
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

    
    # Find ID by USERNAME
    def _id_by_Username(uname: str) -> int:
        result = User.__USER_by_uname(uname)
        if result == -1:
            return result
        return result.id, result.permission


    # Find USERNAME by ID
    def _username_by_id(ID: int):
        result = User.__USER_by_id(ID)
        if result == -1:
            return result
        return result.username, result.permission


    # Check password Hash Validation
    def _validate_password(uname: str, passw: str) -> int:
        result = User.__USER_by_uname(uname)
        if result == -1:
            return result
        if check_password_hash(result.hash, passw):
            return result.id, result.permission
        return -2


    # Insert New USER
    def new_user(uname: str, passw: str, perm: int = 0) -> int:
        TRY = 10
        newUser = User(username = uname, hash = generate_password_hash(passw), permission = perm)
        while True:
            if User.__USER_by_uname(uname) != -1:
                return -1
            db_session.add(newUser)
            try:
                db_session.commit()
                return User._id_by_Username(uname)
            except:
                db_session.rollback()
                print("Wait for connection...")
                if TRY > 0:
                    TRY -= 1
                else:
                    return -2
    

    # Update user USERNAME
    def update_username(uname: str, passw: str, nuname: str) -> int:
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
                return 0
            except:
                db_session.rollback()
                print("Wait for connection...")
                if TRY > 0:
                    TRY -= 1
                else:
                    return -4
    

    # Update user PASSWORD
    def update_password(uname: str, passw: str, npassw: str):
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
                return 0
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
class Reference(Base):
    __tablename__ = 'references'
    id = Column('ref_id', Integer, primary_key=True, nullable=False)
    name = Column('name', String, unique=True, nullable=False)
    value = Column('value', String, unique=True, nullable=False)
    href = Column('href', String, nullable=False)
    create_at = Column('created_at', DateTime, server_default=func.now(), nullable=False)
    updated_at = Column('updated_at', DateTime, server_default=func.now(), nullable=False)
    
    def _refList(act: str):
        REFS = select(Reference)
        REFS = db_session.execute(REFS).all()
        refs = []
        for r in REFS:
            activ = 'active' if act == r[0].name else ''
            tmpDict = {"name": r[0].name, "value": r[0].value, "href": r[0].href, "active": activ}
            refs.append(tmpDict)
        return refs

    def _newRef(rname: str, rvalue: str, rhref: str):
        QUERY = select(Reference).where(or_(Reference.name == rname, Reference.value == rvalue))
        result = db_session.execute(QUERY).first()
        if result:
            return -1
        newref = Reference(name = rname, value = rvalue, href = rhref)
        TRY = 10
        while True:
            db_session.add(newref)
            try:
                db_session.commit()
                return 0
            except:
                db_session.rollback()
                if TRY > 0:
                    TRY -= 1
                else:
                    return -2


# UPLOADIMAGE Object
class upimage(Base):
    __tablename__ = 'upimages'
    id = Column('img_id', Integer, primary_key=True, nullable=False)
    name = Column('name', String, nullable=False)
    blob = Column('blob', BLOB, nullable=False)
    href = Column('href', String, nullable=False)
    create_at = Column('created_at', DateTime, server_default=func.now(), nullable=False)
    updated_at = Column('updated_at', DateTime, server_default=func.now(), nullable=False)
    
