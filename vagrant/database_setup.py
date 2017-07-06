from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Asin(Base):
    __tablename__ = 'asin'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Sku(Base):
    __tablename__ = 'sku'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    asin_id = Column(Integer, ForeignKey('asin.id'))
    asin = relationship(Asin)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id
        }


class Keyword(Base):
    __tablename__ = 'keyword'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    asin_id = Column(Integer, ForeignKey('asin.id'))
    asin = relationship(Asin)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id
        }


engine = create_engine('sqlite:///amazon.db')


Base.metadata.create_all(engine)
