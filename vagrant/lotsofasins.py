from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setupv2 import Asin, Base, Sku, User, Keyword

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
User1 = User(name="Samuel Hong", email="sml.hng@gmail.com")
session.add(User1)
session.commit()

# Menu for UrbanBurger
asin1 = Asin(user_id=1, name="B00KG45W08")

session.add(asin1)
session.commit()

sku1 = Sku(user_id=1, name="Slim 2 Blue", asin=asin1)

session.add(sku1)
session.commit()

keyword1 = Keyword(user_id=1, name="cell phone charger", asin=asin1)

session.add(keyword1)
session.commit()


# Another asin
asin2 = Asin(user_id=1, name="B01G1XH46M")

session.add(asin2)
session.commit()

sku2 = Sku(user_id=1, name="RP-PB052(B)", asin=asin2)

session.add(sku2)
session.commit()

keyword2 = Keyword(user_id=1, name="external battery pack", asin=asin2)

session.add(keyword2)
session.commit()


print "added asins!"
