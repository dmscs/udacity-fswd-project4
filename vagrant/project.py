from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Asin, Base, Sku, User, Keyword

from flask import session as login_session
import random, string

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps


# Decorater to check user is logged in.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Men Application"


#Connect to Database and create database session
engine = create_engine('sqlite:///amazon.db')
Base.metadata.bind = engine


DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create a state token to prevent request forgery.
# Store it in a session for later validation.
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id


    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Attempts gdisconnect. If sucessful, navigates to publicasins.html,
# else returns error message
@app.route('/logout')
def logout():
    response = gdisconnect()
    print response.status
    if response.status == '200 OK':
        asins = session.query(Asin).order_by(asc(Asin.name))
        return render_template('publicasins.html', asins = asins)
    else:
        return response


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
      print 'Access Token is None'
      response = make_response(json.dumps('Current user not connected.'), 401)
      response.headers['Content-Type'] = 'application/json'
      return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
      del login_session['access_token']
      del login_session['gplus_id']
      del login_session['username']
      del login_session['email']
      del login_session['picture']
      response = make_response(json.dumps('Successfully disconnected.'), 200)
      response.headers['Content-Type'] = 'application/json'
      return response
    else:

      response = make_response(json.dumps('Failed to revoke token for given user.', 400))
      response.headers['Content-Type'] = 'application/json'
      return response


#JSON APIs to view Asin, Keyword, and Sku Information
@app.route('/asin/<int:asin_id>/skus/JSON')
def skusJSON(asin_id):
    asin = session.query(Asin).filter_by(id = asin_id).one()
    items = session.query(Sku).filter_by(asin_id = asin_id).all()
    return jsonify(Skus=[i.serialize for i in items])


@app.route('/asin/<int:asin_id>/sku/<int:sku_id>/JSON')
def skuJSON(asin_id, sku_id):
    sku = session.query(Sku).filter_by(id = sku_id).one()
    return jsonify(Sku = sku.serialize)


@app.route('/asin/<int:asin_id>/keywords/JSON')
def keywordsJSON(asin_id):
    asin = session.query(Asin).filter_by(id = asin_id).one()
    items = session.query(Keyword).filter_by(asin_id = asin_id).all()
    return jsonify(Keywords=[i.serialize for i in items])


@app.route('/asin/<int:asin_id>/keyword/<int:keyword_id>/JSON')
def keywordJSON(asin_id, keyword_id):
    keyword = session.query(Keyword).filter_by(id = keyword_id).one()
    return jsonify(Keyword = keyword.serialize)


@app.route('/asins/JSON')
def asinsJSON():
    asins = session.query(Asin).all()
    return jsonify(asins= [r.serialize for r in asins])


@app.route('/asin/<int:asin_id>/JSON')
def asinJSON(asin_id):
    asin = session.query(Asin).filter_by(id = asin_id).one()
    return jsonify(asin= asin.serialize)


#Show all asins
@app.route('/')
@app.route('/asin/')
def showAsins():
    asins = session.query(Asin).order_by(asc(Asin.name))
    if 'username' not in login_session:
        return render_template('publicasins.html', asins = asins)
    else:
        return render_template('asins.html', asins = asins)

#Create a new asin
@app.route('/asin/new/', methods=['GET','POST'])
@login_required
def newAsin():
    if request.method == 'POST':
        newAsin = Asin(name = request.form['name'],
                                   user_id=login_session['user_id'])
        session.add(newAsin)
        flash('New Asin %s Successfully Created' % newAsin.name)
        session.commit()
        return redirect(url_for('showAsins'))
    else:
        return render_template('newAsin.html')

#Edit an asin
@app.route('/asin/<int:asin_id>/edit/', methods = ['GET', 'POST'])
@login_required
def editAsin(asin_id):
    editedAsin = session.query(Asin).filter_by(id = asin_id).one()
    if request.method == 'POST':
        if request.form['name']:
          editedAsin.name = request.form['name']
          flash('Asin Successfully Edited %s' % editedAsin.name)
          return redirect(url_for('showAsins'))
    else:
      return render_template('editAsin.html', asin = editedAsin)


#Delete an asin
@app.route('/asin/<int:asin_id>/delete/', methods = ['GET','POST'])
@login_required
def deleteAsin(asin_id):
    asinToDelete = session.query(Asin).filter_by(id = asin_id).one()
    if asinToDelete.user_id != login_session['user_id']:
        jscript_text = (
        "<script>function myFunction() {alert('You are not authorized "
        "to delete this asin.');}</script>"
        "<body onload='myFunction()''>"
        )
        return jscript_text
    if request.method == 'POST':
      session.delete(asinToDelete)
      flash('%s Successfully Deleted' % asinToDelete.name)
      session.commit()
      return redirect(url_for('showAsins', asin_id = asin_id))
    else:
      return render_template('deleteAsin.html',asin = asinToDelete)

#Show a sku
@app.route('/asin/<int:asin_id>/')
@app.route('/asin/<int:asin_id>/sku/')
def showSku(asin_id):
    asin = session.query(Asin).filter_by(id = asin_id).one()
    creator = getUserInfo(asin.user_id)
    items = session.query(Sku).filter_by(asin_id = asin_id).all()
    keywords = session.query(Keyword).filter_by(asin_id = asin_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicsku.html', keywords = keywords,
                                items = items, asin = asin, creator = creator)
    else:
        return render_template('sku.html', keywords = keywords,
                                items = items, asin = asin, creator = creator)


#Create a new sku
@app.route('/asin/<int:asin_id>/sku/new/',methods=['GET','POST'])
@login_required
def newSku(asin_id):
    asin = session.query(Asin).filter_by(id = asin_id).one()
    if request.method == 'POST':
        newItem = Sku(name = request.form['name'], asin_id = asin_id,
                      user_id = asin.user_id)
        session.add(newItem)
        session.commit()
        flash('New Sku %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showSku', asin_id = asin_id))
    else:
        return render_template('newsku.html', asin_id = asin_id)

#Edit a sku
@app.route('/asin/<int:asin_id>/sku/<int:sku_id>/edit', methods=['GET','POST'])
@login_required
def editSku(asin_id, sku_id):
    editedItem = session.query(Sku).filter_by(id = sku_id).one()
    asin = session.query(Asin).filter_by(id = asin_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        session.add(editedItem)
        session.commit()
        flash('Sku Item Successfully Edited')
        return redirect(url_for('showSku', asin_id = asin_id))
    else:
        return render_template('editskuitem.html', asin_id = asin_id, sku_id = sku_id, item = editedItem)


#Delete a sku
@app.route('/asin/<int:asin_id>/sku/<int:sku_id>/delete', methods = ['GET','POST'])
@login_required
def deleteSku(asin_id,sku_id):
    asin = session.query(Asin).filter_by(id = asin_id).one()
    itemToDelete = session.query(Sku).filter_by(id = sku_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Sku Item Successfully Deleted')
        return redirect(url_for('showSku', asin_id = asin_id))
    else:
        return render_template('deleteSkuItem.html', item = itemToDelete)


#Create a new keyword
@app.route('/asin/<int:asin_id>/keyword/new/',methods=['GET','POST'])
@login_required
def newKeyword(asin_id):
    asin = session.query(Asin).filter_by(id = asin_id).one()
    if request.method == 'POST':
        newItem = Keyword(name = request.form['name'], asin_id = asin_id,
                      user_id = asin.user_id)
        session.add(newItem)
        session.commit()
        flash('New Sku %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showSku', asin_id = asin_id))
    else:
        return render_template('newkeyword.html', asin_id = asin_id)


#Delete a keyword
@app.route('/asin/<int:asin_id>/keyword/<int:keyword_id>/delete', methods = ['GET','POST'])
@login_required
def deleteKeyword(asin_id, keyword_id):
    asin = session.query(Asin).filter_by(id = asin_id).one()
    itemToDelete = session.query(Keyword).filter_by(id = keyword_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Keyword Successfully Deleted')
        return redirect(url_for('showSku', asin_id = asin_id))
    else:
        return render_template('deleteKeyword.html', item = itemToDelete)



if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
