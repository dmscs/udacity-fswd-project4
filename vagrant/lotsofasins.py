from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Asin, Base, Sku, User, Keyword

engine = create_engine('sqlite:///amazon.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="", email="todays.review001@gmail.com")
session.add(User1)
session.commit()

# Menu for UrbanBurger
asin1 = Asin(user_id=1, name="B00KG45W08")

session.add(asin1)
session.commit()

sku1a = Sku(user_id=1, name="Slim 2 Blue", asin=asin1)

session.add(sku1a)
session.commit()

sku1b = Sku(user_id=1, name="sd/wqw/001", asin=asin1)

session.add(sku1b)
session.commit()

keyword1a = Keyword(user_id=1, name="cell phone charger", asin=asin1)

session.add(keyword1a)
session.commit()

keyword1b = Keyword(user_id=1, name="cord for phone", asin=asin1)

session.add(keyword1b)
session.commit()


# Another asin
asin2 = Asin(user_id=1, name="B01G1XH46M")

session.add(asin2)
session.commit()

sku2a = Sku(user_id=1, name="RP-PB052(B)", asin=asin2)

session.add(sku2a)
session.commit()

sku2b = Sku(user_id=1, name="TER-P0023(C)", asin=asin2)

session.add(sku2b)
session.commit()

keyword2a = Keyword(user_id=1, name="external battery pack", asin=asin2)

session.add(keyword2a)
session.commit()

keyword2b = Keyword(user_id=1, name="battery sun powered", asin=asin2)

session.add(keyword2b)
session.commit()


print "added asins!"
