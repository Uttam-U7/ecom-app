from database.data import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    razorpay_order_id = db.Column(
        db.String,
        nullable = True,
        unique = True
    )

    amount = db.Column(
        db.Float,
        nullable = False
    )

    status = db.Column(
        db.String(20),
        nullable = False,
        default = "Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default = datetime.utcnow
    )


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(
        db.Integer, 
        primary_key=True
    )
    order_id = db.Column(
        db.Integer, 
        db.ForeignKey("orders.id"), 
        nullable=False
    )
    product_id = db.Column(
        db.Integer, 
        nullable=False
    )
    sku = db.Column(
        db.String(50), 
        nullable=False
        )
    name = db.Column(
        db.String(200), 
        nullable=False
        )
    price = db.Column(
        db.Integer, 
        nullable=False
    )
    quantity = db.Column(
        db.Integer, 
        nullable=False
    )
    subtotal = db.Column(
        db.Integer, 
        nullable=False
    )

class PaymentDetails(db.Model):
    __tablename__ = "Payment_Details"

    id = db.Column(
        db.Integer, 
        primary_key = True
    )

    order_id = db.Column(
        db.Integer, 
        db.ForeignKey("orders.id"), 
        nullable=False
    )

    payment_id = db.Column(
        db.String, 
        unique = True, 
        nullable = False
    )

    status = db.Column(
        db.String, 
        nullable = False
    )
