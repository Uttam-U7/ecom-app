from database.data import db
from datetime import datetime

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
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )