from flask_login import UserMixin

from catalog_items import db
from catalog_items.models.category import Category
from catalog_items.models.user import User


class Items(UserMixin, db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(250))
    picture = db.Column(db.String(250))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationship
    category = db.relationship(Category, backref=db.backref('items', cascade='all, delete'))
    user = db.relationship(User, backref="items")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'picture': self.picture,
            'category': self.category.name
        }
