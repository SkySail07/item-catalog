from catalog_items import db
from catalog_items.models.category import Category


def get_all_category():
    return Category.query.order_by(Category.name.asc())


def find_by_category_name(category_name):
    return Category.query.filter_by(name=category_name).one()


def find_by_id(category_id):
    return Category.query.get(category_id)


def create_new_category(name, user_id):
    try:
        newCategory = Category(name=name, user_id=user_id)
        print(newCategory)
        db.session.add(newCategory)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
