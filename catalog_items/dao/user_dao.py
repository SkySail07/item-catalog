from catalog_items import db
from catalog_items.models.user import User


def create_user(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'],
                   tokens=login_session['access_token'])
    db.session.add(newUser)
    db.session.commit()
    user = User.query.filter_by(email=login_session['email']).one()
    return user


def get_user(user_id):
    return User.query.filter_by(id=user_id).one()


def find_by_email(email):
    try:
        user = User.query.filter_by(email=email).one()
        return user
    except:
        return None
