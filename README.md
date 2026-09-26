# PayCom — a React + Flask e-commerce demo

A small pour-over coffee gear shop used to demonstrate a full add-to-cart →
checkout flow with a React frontend and a Flask JSON API backend.

ecom-app/
├── backend/          Flask API (products, cart, orders — SQLAlchemy)
│   ├── app.py
│   └── requirements.txt
└── frontend/         React app (Vite)
    └── src/
        ├── api.js                 fetch wrapper for the backend
        ├── context/CartContext.jsx  shared cart state
        ├── components/            Navbar, ProductCard, blueprint icons
        └── pages/                 Home (catalog) and Cart

## What it does

- **Home page** — lists all products as cards. Each card has an
  **Add to Cart** button (adds it to the shared cart) and an **Order Now**
  button (places an instant single-item order, bypassing the cart).
- **Cart page** — shows every item currently in the cart, lets you bump the
  quantity up/down or **remove** a line entirely, computes the running
  total, and has a **Pay Now** button that checks out and clears the cart.
- The catalog is static, while the shared cart and simulated orders are stored
  in SQLAlchemy tables. There's no login, so all clients share one cart.
  "Pay Now" simulates a checkout.

## 1. Run the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The API starts on **http://localhost:5000**. Key endpoints:

| Method | Path |  Purpose |
--------------------------------------------------------------------
| GET    | `/api/products`    | List the catalog|
| GET    | `/api/cart`        | Current cart + total|
| POST   | `/api/cart/add`   | `{product_id, quantity}` — add/increment|
| POST   | `/api/cart/update` | `{product_id, quantity}` — set exact qty (≤0 removes) |
| DELETE | `/api/cart/<product_id>` | Remove a line item   |
| POST   | `/api/checkout`  | Pay for everything in the cart, clears it |
| POST   | `/api/order-now`| `{product_id, quantity}` — instant single-item order |
| GET    | `/api/orders`    | List persisted simulated orders   |

The backend requires `DATABASE_URL` to point to a PostgreSQL database. For
example, in `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/ecom_db
```

Startup creates the `cart_items`, `orders`, and `order_items` tables in
PostgreSQL.

## 2. Run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. Vite's dev server proxies any `/api/*`
request to the Flask backend on port 5000 (see `vite.config.js`), so the
frontend code just calls `fetch("/api/...")` with no hardcoded host.

## Building for production

```bash
cd frontend
npm run build
```

This outputs static files to `frontend/dist/`, which you can serve with
any static host — just make sure `/api` requests are proxied or the API
base URL in `src/api.js` is pointed at your deployed backend.

## Notes / next steps if you extend this

- The cart is currently shared for everyone hitting the API rather than
  per-user — add sessions or auth and a cart owner key for multiple shoppers.
- "Pay Now" uses Razorpay when its credentials and webhook are configured.

## Deployment and security

- Copy `backend/.env.example` to a secret-managed environment. Never commit
  `.env`, database credentials, Razorpay secrets, or an admin token.
- Set `CORS_ORIGINS` to the exact HTTPS origin(s) serving the frontend.
- Run the backend with the included `backend/Procfile` on a Linux host and
  terminate TLS at the hosting platform or reverse proxy.
- `/api/orders` and `/api/order` require the `X-Admin-Token` header and are
  intended only for an internal admin service.
- Configure Razorpay webhooks with `RAZORPAY_WEBHOOK_SECRET` and verify the
  endpoint is reachable over HTTPS.
- This demo has one shared cart and no customer authentication. Do not accept
  real customer data until carts are scoped to authenticated users or signed
  sessions, and a production privacy notice and retention policy are in place.
