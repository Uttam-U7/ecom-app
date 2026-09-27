from datetime import datetime

from database.data import db


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )
    name = db.Column(
        db.String(200),
        nullable=False
    )
    category = db.Column(
        db.String(50),
        nullable=False
    )
    price = db.Column(
        db.Float,
        nullable=False
    )
    description = db.Column(
        db.String(500),
        nullable=True
    )
    specs = db.Column(
        db.JSON,
        nullable=True
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )