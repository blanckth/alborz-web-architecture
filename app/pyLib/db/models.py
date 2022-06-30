from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.sql import *
from sqlalchemy.orm import relationship, backref
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
    name = Column('name', String, unique=True, nullable=False)
    value = Column('value', String, nullable=False)
    href = Column('href', String, nullable=False)
    sub = Column('sub', Integer, nullable=False, server_default=text('0'))
    root = Column('root', Integer, nullable=False, server_default=text('0'))
    create_at = Column('created_at', DateTime, server_default=func.now(), nullable=False)
    updated_at = Column('updated_at', DateTime, server_default=func.now(), nullable=False)
    
    def _id_by_name(rname: str):
        QUERY = select(HReference).where(HReference.name == rname)
        QUERY = db_session.execute(QUERY).first()
        if QUERY:
            return QUERY[0].id
        return -1

    def _ref_by_name(rname: str):
        QUERY = select(HReference).where(HReference.name == rname)
        QUERY = db_session.execute(QUERY).first()
        if QUERY:
            return QUERY[0]
        return -1

    def _ref_by_id(refid: int):
        QUERY = select(HReference).where(HReference.id == refid)
        QUERY = db_session.execute(QUERY).first()
        if QUERY:
            return QUERY[0]
        return -1

    def _subRefs(refid: int):
        subrefs = select(RefCat).where(RefCat.href_id == refid)
        subrefs = db_session.execute(subrefs).all()
        subRes = []
        for ref in subrefs:
            sref = HReference._ref_by_id(int(ref[0].sub_id))
            if int(sref.sub) > 0:
                subb = HReference._subRefs(int(sref.id))
            else:
                subb = []
            tmpSubref = {"name": sref.name, "value": sref.value, "href": sref.href, "active": "", "sub": sref.sub, "subs": subb , "root": refid}
            subRes.append(tmpSubref)
        return subRes

    def _hrefList(act: str, isAd: int = 0):
        REFS = select(HReference).where(HReference.root == 0)
        REFS = db_session.execute(REFS).all()
        refs = []
        for r in REFS:
            activ = 'active' if act == r[0].name else ''
            subrefss = HReference._subRefs(int(r[0].id)) if int(r[0].sub) > 0 else []
            tmpDict = {"name": r[0].name, "value": r[0].value, "href": r[0].href, "active": activ, "sub": r[0].sub, "subs": subrefss, "root": r[0].root}
            refs.append(tmpDict)
        if isAd:
            REFS = select(HReference).where(HReference.root == -1)
            REFS = db_session.execute(REFS).all()
            for rr in REFS:
                activ = 'active' if act == rr[0].name else ''
                subrefss = HReference._subRefs(int(rr[0].id)) if int(rr[0].sub) > 0 else []
                tmpDict = {"name": rr[0].name, "value": rr[0].value, "href": rr[0].href, "active": activ, "sub": rr[0].sub, "subs": subrefss, "root": rr[0].root}
                refs.append(tmpDict)
        return refs

    
    def _newRef(rname: str, rvalue: str, rhref: str, rroot: int = 0):
        if HReference._id_by_name(rname) != -1:
            return -1
        if rroot > 0:
            rt = HReference._ref_by_id(rroot)
            if rt == -1:
                return -2
        newref = HReference(name = rname, value = rvalue, href = rhref, root = rroot)
        TRY = 10
        while True:
            if HReference._id_by_name(rname) != -1:
                return -3
            db_session.add(newref)
            try:
                db_session.commit()
                newref = HReference._ref_by_name(rname)
                if rroot > 0:
                    rc = RefCat._newCat(rroot, newref.id)
                    if rc < 0:
                        return -4 
                return newref
            except:
                db_session.rollback()
                if TRY > 0:
                    TRY -= 1
                else:
                    return -5

# REFERENCES CATEGORY
class RefCat(Base):

    __tablename__ = 'refcats'

    id = Column('refcat_id', Integer, primary_key=True, nullable=False)
    href_id = Column('href_id', Integer, nullable=False)
    sub_id = Column('sub_id', Integer, nullable=False)

    def _newCat(refid: int, subid: int):
        ref = HReference._ref_by_id(refid)
        if ref == -1:
            return -2
        subr = HReference._ref_by_id(subid)
        if subr == -1:
            return -3
        ncr = RefCat(href_id = refid, sub_id = subid)
        TRY = 10
        while True:
            db_session.add(ncr)
            ref.sub = int(ref.sub) + 1
            try:
                db_session.commit()
                return 0
            except:
                db_session.rollback()
                if TRY > 0:
                    TRY -= 1
                else:
                    return -4

class ImgCat(Base):

    __tablename__ = 'imgcats'
    id = Column('imgcat_id', Integer, primary_key=True, nullable=False)
    name = Column('name', String, unique=True, nullable=False)
    value = Column('value', String, unique=True, nullable=False)

    def ic_by_id(icid):
        QUERY = select(ImgCat).where(ImgCat.id == icid)
        QUERY = db_session.execute(QUERY).first()
        if QUERY:
            return QUERY[0]
        return -1

    def ic_by_name(icname):
        QUERY = select(ImgCat).where(ImgCat.name == icname)
        QUERY = db_session.execute(QUERY).first()
        if QUERY:
            return QUERY[0]
        return -1

    def ic_by_val(icval):
        QUERY = select(ImgCat).where(ImgCat.value == icval)
        QUERY = db_session.execute(QUERY).first()
        if QUERY:
            return QUERY[0]
        return -1

    def _ic_list():
        QUERY = select(ImgCat)
        QUERY = db_session.execute(QUERY).all()
        if QUERY:
            return QUERY
        return -1

    def _new_icat(icn: str, icval: str):
        if ImgCat.ic_by_name(icn) != -1:
            return -1
        if ImgCat.ic_by_val(icval) != -1:
            return -2
        newic = ImgCat(name = icn, value = icval)
        TRY = 10
        while True:
            db_session.add(newic)
            try:
                db_session.commit()
                return 0
            except:
                db_session.rollback()
                if TRY > 0:
                    TRY -= 1
                else:
                    return -3


class ImgRef(Base):

    __tablename__ = 'imgrefs'

    id = Column('imgref_id', Integer, primary_key=True, nullable=False)
    name = Column('name', String, unique=True, nullable=False)
    href = Column('href', String, nullable=False)
    morehref = Column('morehref', String, nullable=False, server_default='#')
    alt = Column('alt', String, nullable=False, server_default='image')
    title = Column('title', String, nullable=False, server_default='title')
    keyword = Column('keyword', String, nullable=False, server_default='keyword')
    addg = Column('addtog', Integer, nullable=False, server_default=text('0'))
    imgcat_id = Column('imgcat_id', Integer, ForeignKey('imgcats.imgcat_id'), nullable=False)
    imgcats = relationship("ImgCat", backref=backref("imgcats", uselist=False))


    def _img_by_name(iname):
        QUERY = select(ImgRef).where(ImgRef.name == iname)
        QUERY = db_session.execute(QUERY).first()
        if QUERY:
            return QUERY[0]
        return -1

    def _img_by_id(iid):
        QUERY = select(ImgRef).where(ImgRef.id == iid)
        QUERY = db_session.execute(QUERY).first()
        if QUERY:
            return QUERY[0]
        return -1

    def _new_img(iname: str, ihref: str, ialt: str = 'image', imorehref: str = '#', iaddg: int = 0, ititle: str = 'Title', icat: str = 'general' , ikeyword: str = 'Keyword'):
        if ImgRef._img_by_name(iname) != -1:
            return -1
        imcat = ImgCat.ic_by_name(icat)
        if icat == -1:
            return -2
        newimg = ImgRef(name = iname, href = ihref, alt = ialt, morehref = imorehref, addg = iaddg, title = ititle, keyword = ikeyword, imgcat_id = int(imcat.id))
        TRY = 10
        while True:
            db_session.add(newimg)
            try:
                db_session.commit()
                return ImgRef._img_by_name(iname)
            except:
                db_session.rollback()
                if TRY > 0:
                    TRY -= 1
                else:
                    return -2

    def _img_list():
        QUERY = select(ImgRef)
        QUERY = db_session.execute(QUERY).all()
        if not QUERY:
            return -1
        imgs = []
        for i in QUERY:
            tmpID = {'id': i[0].id, 'name': i[0].name, 'href': i[0].href, 'cat': i[0].imgcats.name, 'gal': int(i[0].addg), 'title': i[0].title, 'kword': i[0].keyword}
            imgs.append(tmpID)
        return imgs

