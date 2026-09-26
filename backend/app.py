
from flask import Flask, jsonify, request
from flask_cors import CORS
import razorpay
from database.data import db
from dotenv import load_dotenv
from models.cart import CartItem
from models.order import Order, OrderItem, PaymentDetails
import os
import hmac
import hashlib

load_dotenv()

app = Flask(__name__)
app.config.update(
    MAX_CONTENT_LENGTH=16 * 1024,
    JSON_SORT_KEYS=False,
)

cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "https://ecom-app-integratee.vercel.app/").split(",") if origin.strip()]
CORS(app, resources={r"/api/*": {"origins": cors_origins}})

razorpay_key_id = os.getenv("RAZORPAY_TEST_KEY_ID")
razorpay_secret = os.getenv("RAZORPAY_TEST_SECRET")
if not razorpay_key_id or not razorpay_secret:
    raise RuntimeError("RAZORPAY_TEST_KEY_ID and RAZORPAY_TEST_SECRET must be set")
razorpay_client = razorpay.Client(auth=(razorpay_key_id, razorpay_secret))

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL must be set to a PostgreSQL connection URL")
if not database_url.startswith(("postgresql://", "postgresql+psycopg2://")):
    raise RuntimeError("DATABASE_URL must use PostgreSQL")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if request.is_secure:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


@app.errorhandler(413)
def request_too_large(_error):
    return jsonify({"error": "Request body is too large"}), 413


def require_admin_token():
    expected_token = os.getenv("ADMIN_API_TOKEN")
    provided_token = request.headers.get("X-Admin-Token")
    if not expected_token or not provided_token or not hmac.compare_digest(provided_token, expected_token):
        return jsonify({"error": "Unauthorized"}), 401
    return None

with app.app_context():
    db.create_all()

# ---------------------------------------------------------------------------
# Data — the catalog is static for this demo; cart and orders are persisted.
# ---------------------------------------------------------------------------
PRODUCTS = [
    {
        "id": 1,
        "img" : "https://unsplash.com/photos/tree-before-building-with-dark-louvers-5dJgpTBw--w",
        "sku": "KG-DR01",
        "name": "Kalita Wave Dripper",
        "category": "dripper",
        "price": 2499,
        "description": "Flat-bottom pour-over dripper for even, repeatable extraction.",
        "specs": {"Material": "Ceramic", "Origin": "Japan", "Weight": "320 g"},
    },
    {
        "id": 2,
        "img" : "https://unsplash.com/photos/tree-before-building-with-dark-louvers-5dJgpTBw--w",
        "sku": "KG-GR02",
        "name": "Comandante C40 Grinder",
        "category": "grinder",
        "price": 10999,
        "description": "Hand grinder with hardened-steel conical burrs.",
        "specs": {"Material": "Stainless steel", "Origin": "Germany", "Weight": "460 g"},
    },
    {
        "id": 3,
        "img" : "https://unsplash.com/photos/tree-before-building-with-dark-louvers-5dJgpTBw--w",
        "sku": "KG-KT03",
        "name": "Fellow Stagg EKG Kettle",
        "category": "kettle",
        "price": 8999,
        "description": "Variable-temperature gooseneck kettle with LCD display.",
        "specs": {"Material": "Stainless steel", "Origin": "USA", "Weight": "1.1 kg"},
    },
    {
        "id": 4,
        "img" : "https://www.nintendo.com/au/news-and-articles/get-to-know-link-and-his-many-adventures/?srsltid=AfmBOori9ske8vaFf8J09xFJ9aYDs8M4-6gOgRKZCxiBVJzUSuL1wkly",
        "sku": "KG-SC04",
        "name": "Acaia Pearl Scale",
        "category": "scale",
        "price": 12499,
        "description": "0.1 g precision scale with a built-in brew timer.",
        "specs": {"Material": "Aluminium", "Origin": "Taiwan", "Weight": "370 g"},
    },
    {
        "id": 5,
        "img" : "https://www.nintendo.com/au/news-and-articles/get-to-know-link-and-his-many-adventures/?srsltid=AfmBOori9ske8vaFf8J09xFJ9aYDs8M4-6gOgRKZCxiBVJzUSuL1wkly",
        "sku": "KG-CF05",
        "name": "Chemex Six-Cup Carafe",
        "category": "carafe",
        "price": 4299,
        "description": "Iconic hourglass carafe for a clean, bright cup.",
        "specs": {"Material": "Borosilicate glass", "Origin": "USA", "Weight": "482 g"},
    },
    {
        "id": 6,
        "img" : "https://www.nintendo.com/au/news-and-articles/get-to-know-link-and-his-many-adventures/?srsltid=AfmBOori9ske8vaFf8J09xFJ9aYDs8M4-6gOgRKZCxiBVJzUSuL1wkly",
        "sku": "KG-FL06",
        "name": "Hario V60 Filters (100 ct)",
        "category": "filters",
        "price": 449,
        "description": "Tabbed paper filters sized for the V60-02 dripper.",
        "specs": {"Material": "Paper", "Origin": "Japan", "Weight": "180 g"},
    },
]

PRODUCTS_BY_ID = {p["id"]: p for p in PRODUCTS}

def get_product_or_404(product_id):
    product = PRODUCTS_BY_ID.get(product_id)
    if product is None:
        return None
    return product


def serialize_cart():
    """Build the cart response: line items with computed subtotal, plus total."""
    items = []
    total = 0
    for cart_item in CartItem.query.order_by(CartItem.product_id).all():
        product_id = cart_item.product_id
        quantity = cart_item.quantity
        product = PRODUCTS_BY_ID.get(product_id)
        if not product or quantity <= 0:
            continue
        subtotal = product["price"] * quantity
        total += subtotal
        items.append({
            "img":product["img"],
            "product_id": product["id"],
            "sku": product["sku"],
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity,
            "subtotal": subtotal,
        })
    return {"items": items, "total": total, "count": sum(i["quantity"] for i in items)}


def create_order_record(items, status="PAID", razorpay_order_id=None):
    total = sum(item["subtotal"] for item in items)
    order = Order(razorpay_order_id=razorpay_order_id, amount=total, status=status)
    db.session.add(order)
    db.session.flush()
    for item in items:
        db.session.add(OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            sku=item["sku"],
            name=item["name"],
            price=item["price"],
            quantity=item["quantity"],
            subtotal=item["subtotal"],
        ))
    db.session.commit()
    return order


def serialize_order(order):
    items = [
        {
            "product_id": item.product_id,
            "sku": item.sku,
            "name": item.name,
            "price": item.price,
            "quantity": item.quantity,
            "subtotal": item.subtotal,
        }
        for item in OrderItem.query.filter_by(order_id=order.id).all()
    ]
    return {
        "order_id": order.razorpay_order_id or str(order.id),
        "items": items,
        "total": order.amount,
        "status": order.status,
    }


# ---------------------------------------------------------------------------
# Routes

# ---------------------------------------------------------------------------

@app.get("/")
def index():
    return jsonify({"message": "Welcome to the E-Commerce API"})

@app.get("/api/products")

def list_products():
    return jsonify(PRODUCTS)


@app.get("/api/products/<int:product_id>")
def get_product(product_id):
    product = get_product_or_404(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product)

@app.get("/api/order")
def get_orders():
    unauthorized = require_admin_token()
    if unauthorized:
        return unauthorized
    orders = Order.query.all()
    return jsonify([serialize_order(order) for order in orders])

@app.get("/api/cart")
def get_cart():
    return jsonify(serialize_cart())


@app.post("/api/cart/add")
def add_to_cart():
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    try:
        quantity = int(data.get("quantity", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "quantity must be a positive integer"}), 400

    if product_id is None or not get_product_or_404(product_id):
        return jsonify({"error": "Unknown product_id"}), 400
    if quantity < 1:
        return jsonify({"error": "quantity must be at least 1"}), 400

    cart_item = CartItem.query.filter_by(product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        db.session.add(CartItem(product_id=product_id, quantity=quantity))
    db.session.commit()
    return jsonify(serialize_cart())


@app.post("/api/cart/update")
def update_cart_item():
    """Set a line item to an exact quantity. quantity <= 0 removes it."""
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    try:
        quantity = int(data.get("quantity", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "quantity must be an integer"}), 400

    if product_id is None or not get_product_or_404(product_id):
        return jsonify({"error": "Unknown product_id"}), 400

    if quantity <= 0:
        CartItem.query.filter_by(product_id=product_id).delete()
    else:
        cart_item = CartItem.query.filter_by(product_id=product_id).first()
        if cart_item:
            cart_item.quantity = quantity
        else:
            db.session.add(CartItem(product_id=product_id, quantity=quantity))
    db.session.commit()
    return jsonify(serialize_cart())


@app.delete("/api/cart/<int:product_id>")
def remove_from_cart(product_id):
    CartItem.query.filter_by(product_id=product_id).delete()
    db.session.commit()
    return jsonify(serialize_cart())


@app.post("/api/cart/clear")
def clear_cart():
    CartItem.query.delete()
    db.session.commit()
    return jsonify(serialize_cart())


@app.post("/api/checkout")
def checkout():
    """Pay for everything currently in the cart."""
    cart = serialize_cart()
    if not cart["items"]:
        return jsonify({"error": "Cart is empty"}), 400

    order = create_order_record(cart["items"])
    CartItem.query.delete()
    db.session.commit()
    return jsonify(serialize_order(order))

@app.post("/api/create-order")
def create_order():
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    try:
        quantity = int(data.get("quantity", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "quantity must be a positive integer"}), 400

    product = get_product_or_404(product_id) if product_id is not None else None
    if not product:
        return jsonify({"error": "Unknown product_id"}), 400
    if quantity < 1:
        return jsonify({"error": "quantity must be at least 1"}), 400

    subtotal = product["price"] * quantity * 100
    order_data = {
        "amount": subtotal,
        "currency": "INR",
        "receipt": f"product-{product_id}",
    }

    try:
        razorpay_order = razorpay_client.order.create(data=order_data)
    except Exception:
        app.logger.exception("Razorpay order creation failed")
        return jsonify({"error": "Unable to create payment order"}), 502

    try:
        order = Order(
            razorpay_order_id=razorpay_order["id"],
            amount=subtotal,
            status="PENDING"
        )
        db.session.add(order)
        db.session.commit()
        db.session.refresh(order)
        db.session.add(OrderItem(
            order_id=order.id,
            product_id=product["id"],
            sku=product["sku"],
            name=product["name"],
            price=product["price"],
            quantity=quantity,
            subtotal=product["price"] * quantity,
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()
        app.logger.exception("Order persistence failed")
        return jsonify({"error": "Unable to save order"}), 500

    return jsonify({
        "order_id": razorpay_order["id"],
        "amount": subtotal,
        "currency": "INR",
        "key_id": razorpay_key_id,
    })

@app.post("/api/create-cart-order")
def create_cart_order():
    """Create a Razorpay order for everything currently in the cart."""
    cart = serialize_cart()
    if not cart["items"]:
        return jsonify({"error": "Cart is empty"}), 400

    amount = cart["total"] * 100
    try:
        razorpay_order = razorpay_client.order.create(data={
            "amount": amount,
            "currency": "INR",
            "receipt": "cart-order",
        })
    except Exception:
        app.logger.exception("Razorpay cart order creation failed")
        return jsonify({"error": "Unable to create payment order"}), 502

    try:
        order = Order(
            razorpay_order_id=razorpay_order["id"],
            amount=cart["total"],
            status="PENDING",
        )
        db.session.add(order)
        db.session.flush()
        for item in cart["items"]:
            db.session.add(OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                sku=item["sku"],
                name=item["name"],
                price=item["price"],
                quantity=item["quantity"],
                subtotal=item["subtotal"],
            ))
        db.session.commit()
    except Exception:
        db.session.rollback()
        app.logger.exception("Cart order persistence failed")
        return jsonify({"error": "Unable to save order"}), 500

    return jsonify({
        "order_id": razorpay_order["id"],
        "amount": amount,
        "currency": "INR",
        "key_id": razorpay_key_id,
    })

@app.post("/api/verify")
def verify_signature():

    data = request.get_json(silent=True) or request.form.to_dict()

    payment_id = data.get("razorpay_payment_id")
    order_id = data.get("razorpay_order_id")
    signature = data.get("razorpay_signature")

    if not all([payment_id, order_id, signature]):
        return jsonify({
            "error": "Missing payment verification data"
        }), 400

    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        })

    except Exception:
        return jsonify({
            "error": "Invalid payment signature"
        }), 400

    order = Order.query.filter_by(razorpay_order_id=order_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404
    order.status = "PAID"
    if not PaymentDetails.query.filter_by(payment_id=payment_id).first():
        db.session.add(PaymentDetails(order_id=order.id, payment_id=payment_id, status="Success"))
    db.session.commit()

    return jsonify({
        "message": "Payment verification successful",
        "order_id": order_id,
    }), 200


@app.post("/api/order-now")
def order_now():
    """Buy a single product immediately, bypassing the cart."""
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    try:
        quantity = int(data.get("quantity", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "quantity must be a positive integer"}), 400

    product = get_product_or_404(product_id) if product_id is not None else None
    if not product:
        return jsonify({"error": "Unknown product_id"}), 400
    if quantity < 1:
        return jsonify({"error": "quantity must be at least 1"}), 400

    subtotal = product["price"] * quantity

    items = [{
            "product_id": product["id"],
            "sku": product["sku"],
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity,
            "subtotal": subtotal,
        }]
    order = create_order_record(items)
    return jsonify(serialize_order(order))


@app.get("/api/orders")
def list_orders():
    unauthorized = require_admin_token()
    if unauthorized:
        return unauthorized
    return jsonify([serialize_order(order) for order in Order.query.all()])

@app.post("/webhook")
def razorpay_webhook():
    payload = request.get_data()
    received_signature = request.headers.get("X-Razorpay-Signature")
    if not received_signature:
        return jsonify({"error": "Missing signature"}), 400

    webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")
    if not webhook_secret:
        app.logger.error("RAZORPAY_WEBHOOK_SECRET is not configured")
        return jsonify({"error": "Webhook is not configured"}), 500

    expected_signature = hmac.new(
        webhook_secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected_signature, received_signature):
        return jsonify({"error": "Invalid webhook signature"}), 400

    data = request.get_json(silent=True) or {}
    event = data.get("event")
    if event == "payment.captured":
        payment_entity = data.get("payload", {}).get("payment", {}).get("entity", {})
        razorpay_order_id = payment_entity.get("order_id")
        payment_id = payment_entity.get("id")
        if not razorpay_order_id or not payment_id:
            return jsonify({"error": "Incomplete payment payload"}), 400

        with db.session.begin():

            order = (
                db.session.query(Order)
                .filter_by(razorpay_order_id=razorpay_order_id)
                .with_for_update()
                .first()
            )
            if not order:
                return jsonify({"error": "order not found"}), 404

            order.status = "PAID"
            if not PaymentDetails.query.filter_by(payment_id=payment_id).first():
                db.session.add(PaymentDetails(
                    order_id=order.id,
                    payment_id=payment_id,
                    status="Success",
                ))

    return jsonify({"message": "Webhook processed"}), 200


if __name__ == "__main__":
    app.run(debug=False, port=5000)
