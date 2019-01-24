from catalog_items import db
from catalog_items.models.item import Items


def get_all_items():
    return Items.query.all()


def get_limited_items(limit=5):
    return Items.query.order_by(Items.date.desc()).limit(limit)


def find_by_category(category):
    return Items.query.filter_by(category=category).order_by(Items.name.asc()).all()


def find_by_category_id(category_id):
    return Items.query.filter_by(category_id=category_id).order_by(Items.name.asc()).all()


def find_by_item_name(item_name):
    return Items.query.filter_by(name=item_name).one()


def find_item_in_category_using_name(item_name, category):
    return Items.query.filter_by(name=item_name, category=category).one()


def add_new_item(name, description, picture, category, date, user_id):
    try:
        newItem = Items(name=name,
                        description=description,
                        picture=picture,
                        category=category,
                        date=date,
                        user_id=user_id)
        db.session.add(newItem)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
