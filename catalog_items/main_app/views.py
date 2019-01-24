import json
import os
import datetime

from flask import render_template, redirect, url_for, flash, jsonify
from flask import session as login_session
from flask_login import login_required
from flask import request

from catalog_items import db
from catalog_items.dao import category_dao, item_dao, user_dao
from . import main_blueprint

basedir = os.path.abspath(os.path.dirname(__file__))


@main_blueprint.route('/')
@main_blueprint.route('/catalog/')
def showCatalog():
    categories = category_dao.get_all_category()
    items = item_dao.get_limited_items()
    return render_template('catalog.html', categories=categories, items=items)


# Category Items
@main_blueprint.route('/catalog/<path:category_name>/items/')
def showCategory(category_name):
    categories = category_dao.get_all_category()
    category = category_dao.find_by_category_name(category_name)
    items = item_dao.find_by_category(category)
    print(items)
    count = len(items)
    print('count: {}'.format(count))
    return render_template('items.html',
                           category=category.name,
                           categories=categories,
                           items=items,
                           count=count)


# Display a Specific Item
@main_blueprint.route('/catalog/<path:category_name>/item/<path:item_name>/')
def showItem(category_name, item_name):
    item = item_dao.find_by_item_name(item_name)
    categories = category_dao.get_all_category()
    return render_template('itemdetail.html',
                           item=item,
                           category=category_name,
                           categories=categories)


# Add a category
@main_blueprint.route('/catalog/addcategory', methods=['GET', 'POST'])
@login_required
def addCategory():
    if request.method == 'POST':
        category_name = request.form['name']
        if not category_name.strip():
            flash('Category name cannot be empty')
            return render_template('addcategory.html')
        category_dao.create_new_category(category_name, login_session['user_id'])
        flash('Category Successfully Added!')
        return redirect(url_for('main_app.showCatalog'))
    else:
        return render_template('addcategory.html')


# Edit a category
@main_blueprint.route('/catalog/<path:category_name>/edit', methods=['GET', 'POST'])
@login_required
def editCategory(category_name):
    print(category_name)
    editedCategory = category_dao.find_by_category_name(category_name)
    category = category_dao.find_by_category_name(category_name)

    # See if the logged in user is the owner of item
    creator = get_user_info(editedCategory.user_id)
    user = get_user_info(login_session['user_id'])

    # If logged in user != item owner redirect them
    if creator.id != int(login_session['user_id']):
        flash("You cannot edit this Category. This Category belongs to %s (%s)"
              % (creator.name, creator.email))
        return redirect(url_for('main_app.showCatalog'))
    # POST methods
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        db.session.add(editedCategory)
        db.session.commit()
        flash('Category Item Successfully Edited!')
        return redirect(url_for('main_app.showCatalog'))
    else:
        return render_template('editcategory.html', categories=editedCategory, category=category)


# Delete a category
@main_blueprint.route('/catalog/<path:category_name>/delete', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_name):
    categoryToDelete = category_dao.find_by_category_name(category_name)

    # See if the logged in user is the owner of item
    creator = get_user_info(categoryToDelete.user_id)
    user = get_user_info(login_session['user_id'])

    # If logged in user != item owner redirect them
    if creator.id != int(login_session['user_id']):
        flash("You cannot delete this Category. This Category belongs to %s (%s)"
              % (creator.name, creator.email))
        return redirect(url_for('main_app.showCatalog'))
    if request.method == 'POST':
        db.session.delete(categoryToDelete)
        db.session.commit()
        flash('Category Successfully Deleted! ' + categoryToDelete.name)
        return redirect(url_for('main_app.showCatalog'))
    else:
        return render_template('deletecategory.html', category=categoryToDelete)


# Add an item
@main_blueprint.route('/catalog/add', methods=['GET', 'POST'])
@login_required
def addItem():
    categories = category_dao.get_all_category()
    if request.method == 'POST':
        if 'name' not in request.form or not request.form['name'].strip():
            flash("Item name cannot be empty")
            return render_template('additem.html', categories=categories)
        if 'category' not in request.form:
            flash("Category cannot be empty")
            return render_template('additem.html', categories=categories)
        category = category_dao.find_by_category_name(request.form['category'])
        item_dao.add_new_item(name=request.form['name'],
                              description=request.form['description'],
                              picture=request.form['picture'],
                              category=category,
                              date=datetime.datetime.now(),
                              user_id=login_session['user_id'])
        flash('Item Successfully Added!')
        return redirect(url_for('main_app.showCatalog'))
    else:
        return render_template('additem.html', categories=categories)


# Edit an item
@main_blueprint.route('/catalog/<path:category_name>/item/<path:item_name>/edit',
                      methods=['GET', 'POST'])
@login_required
def editItem(category_name, item_name):
    editedItem = item_dao.find_by_item_name(item_name)
    categories = category_dao.get_all_category()

    # See if the logged in user is the owner of item
    creator = get_user_info(editedItem.user_id)
    user = get_user_info(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != int(login_session['user_id']):
        flash("You cannot edit this item. This item belongs to %s (%s)"
              % (creator.name, creator.email))
        return redirect(url_for('main_app.showCatalog'))
    # POST methods
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['picture']:
            editedItem.picture = request.form['picture']
        if request.form['category']:
            # category = session.query(Category).filter_by(name=request.form['category']).one()
            category = category_dao.find_by_category_name(category_name)
            editedItem.category = category
        time = datetime.datetime.now()
        editedItem.date = time
        db.session.add(editedItem)
        db.session.commit()
        flash('Category Item Successfully Edited!')
        return redirect(url_for('main_app.showCategory', category_name=editedItem.category.name))
    else:
        return render_template('edititem.html', item=editedItem, categories=categories)


# Delete an item
@main_blueprint.route('/catalog/<path:category_name>/item/<path:item_name>/delete',
                      methods=['GET', 'POST'])
@login_required
def deleteItem(category_name, item_name):
    itemToDelete = item_dao.find_by_item_name(item_name)
    category = category_dao.find_by_category_name(category_name)
    # categories = session.query(Category).all()

    # See if the logged in user is the owner of item
    creator = get_user_info(itemToDelete.user_id)
    user = get_user_info(login_session['user_id'])

    # If logged in user != item owner redirect them
    if creator.id != int(login_session['user_id']):
        flash("You cannot delete this item. This item belongs to %s (%s)"
              % (creator.name, creator.email))
        return redirect(url_for('main_app.showCatalog'))

    if request.method == 'POST':
        db.session.delete(itemToDelete)
        db.session.commit()
        flash('Item Successfully Deleted! ' + itemToDelete.name)
        return redirect(url_for('main_app.showCategory', category_name=category.name))
    else:
        return render_template('deleteitem.html', item=itemToDelete)


# ===================
# JSON
# ===================
@main_blueprint.route('/json_viewer')
def json_viewer():
    json_data = None
    if 'json_data' in request.args:
        json_data = request.args['json_data']
    categories = category_dao.get_all_category()
    items = item_dao.get_all_items()
    return render_template("json_view.html",
                           categories=categories,
                           items=items,
                           json_data=json_data)


@main_blueprint.route('/JSON')
def all_category_items_json():
    json_data = dict()
    categories = category_dao.get_all_category()
    category_dict = [c.serialize for c in categories]
    for c in range(len(category_dict)):
        items = [i.serialize for i in item_dao.find_by_category_id(category_dict[c]["id"])]
        if items:
            category_dict[c]["Item"] = items
    json_data['Category'] = category_dict
    return redirect(url_for('main_app.json_viewer', json_data=to_pretty_json(json_data)))


@main_blueprint.route('/JSON/categories')
def categories_json():
    json_data = dict()
    categories = category_dao.get_all_category()
    json_data['categories'] = [c.serialize for c in categories]
    return redirect(url_for('main_app.json_viewer', json_data=to_pretty_json(json_data)))


@main_blueprint.route('/JSON/items')
def items_json():
    json_data = dict()
    items = item_dao.get_all_items()
    json_data['items'] = [i.serialize for i in items]
    return redirect(url_for('main_app.json_viewer', json_data=to_pretty_json(json_data)))


@main_blueprint.route('/JSON/category/<path:category_name>')
def category_items_json(category_name):
    json_data = dict()
    category = category_dao.find_by_category_name(category_name)
    items = item_dao.find_by_category(category)
    json_data['items'] = [i.serialize for i in items]
    return redirect(url_for('main_app.json_viewer', json_data=to_pretty_json(json_data)))


@main_blueprint.route('/JSON/category/<path:category_id>/item/<path:item_name>')
def item_json(category_id, item_name):
    json_data = dict()
    category = category_dao.find_by_id(category_id)
    item = item_dao.find_item_in_category_using_name(item_name, category)
    json_data['item'] = [item.serialize]
    return redirect(url_for('main_app.json_viewer', json_data=to_pretty_json(json_data)))


# url_for static path processor
# remove when deployed
@main_blueprint.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    print(endpoint)
    print(values)
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(basedir,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


def get_user_info(user_id):
    user = user_dao.get_user(user_id)
    return user


def to_pretty_json(value):
    return json.dumps(value, sort_keys=True, indent=4, separators=(',', ': '))
