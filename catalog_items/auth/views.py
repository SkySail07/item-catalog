import json

import httplib2
from flask import render_template, request, url_for, flash, make_response
from flask import session as login_session
from flask_login import current_user, login_user, logout_user
from requests_oauthlib import OAuth2Session
from werkzeug.utils import redirect

from catalog_items import db
from catalog_items.dao import user_dao
from config import Auth
from . import auth_blueprint


# Login - Create anti-forgery state token
@auth_blueprint.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_app.showCatalog'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(Auth.AUTH_URI, access_type='offline')
    login_session['oauth_state'] = state
    return render_template('login.html', auth_url=auth_url)


@auth_blueprint.route('/gconnect')
def callback():
    # Redirect user to home page if already logged in.
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('main_app.showCatalog'))
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('auth.login'))
    # Execution reaches here when user has
    # successfully authenticated our app.
    google = get_google_auth(state=login_session['oauth_state'])
    try:
        token = google.fetch_token(Auth.TOKEN_URI,
                                   client_id=Auth.CLIENT_ID,
                                   client_secret=Auth.CLIENT_SECRET,
                                   authorization_response=request.url)
    except Exception as e:
        print(e)
        return 'HTTPError occurred.'
    google = get_google_auth(token=token)
    resp = google.get(Auth.USER_INFO)
    if resp.status_code == 200:
        user_data = resp.json()

        login_session['username'] = user_data['name']
        login_session['picture'] = user_data['picture']
        login_session['email'] = user_data['email']
        login_session['access_token'] = token.get('access_token')

        # see if user exists, if it doesn't make a new one
        user = user_dao.find_by_email(login_session['email'])
        if not user:
            user = user_dao.create_user(login_session)
        else:
            user.tokens = login_session['access_token']
            db.session.add(user)
            db.session.commit()
        login_session['user_id'] = user.id
        print(token)
        login_user(user)
        flash("you are now logged in as %s" % login_session['username'])
        return redirect(url_for('main_app.showCatalog'))
    return 'Could not fetch your information.'


def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(Auth.CLIENT_ID, state=state, redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(Auth.CLIENT_ID, redirect_uri=Auth.REDIRECT_URI, scope=Auth.SCOPE)
    return oauth


# DISCONNECT - Revoke a current user's token and reset their login_session


@auth_blueprint.route('/gdisconnect')
def gdisconnect():
    logout_user()
    # Only disconnect a connected user.
    token = login_session.get('access_token')
    if token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        # response = make_response(json.dumps('Successfully disconnected.'), 200)
        # response.headers['Content-Type'] = 'application/json'
        response = redirect(url_for('main_app.showCatalog'))
        flash("You are now logged out.")
        return response
    # For whatever reason, the given token was invalid.
    response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
    response.headers['Content-Type'] = 'application/json'
    return response
