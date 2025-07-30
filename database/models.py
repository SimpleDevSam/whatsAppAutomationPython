from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    apidifyBot = Column(String)
    tokenInstance = Column(String)
    whatsappNumber = Column(String, unique=True)
    status = Column(Integer, default=1)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    isBotActive = Column(Integer, default=1)
    conversationId = Column(String, unique=True)
    whatsappNumber = Column(String, unique=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    status = Column(Integer, default=1)
    # sent_images = relationship("sent_images", backref="users", cascade="all, delete-orphan")

class Images(Base):
    __tablename__ = 'images'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    imageUrl = Column(String, unique=True)
    name = Column(String)
    company_id = Column(Integer, ForeignKey('companies.id'))

class SentImages(Base):
    __tablename__ = 'sent_images'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    imageUrl = Column(String, unique=True)
    name = Column(String)
    company_id = Column(Integer, ForeignKey('companies.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
