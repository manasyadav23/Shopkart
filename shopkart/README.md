# 🛒 ShopKart — Flipkart-style E-Commerce App

A full-featured e-commerce web application built with **Flask + SQLite + Bootstrap 5**.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install flask werkzeug
```

### 2. Run the App
```bash
cd shopkart
python app.py
```

### 3. Open in Browser
```
http://localhost:5000
```

---

## 🔐 Demo Accounts

| Role   | Email                  | Password   |
|--------|------------------------|------------|
| Buyer  | user@shopkart.com      | user123    |
| Seller | admin@shopkart.com     | admin123   |

Or use the **"Demo Accounts"** buttons on the login page.

---

## ✨ Features

### 🛍️ Buyer Features
- Browse products in Flipkart-style card grid
- Search by name, brand, or keyword
- Filter by category and price range
- Sort by price, rating, or newest
- Product detail page with description, ratings & reviews
- Add to Cart with quantity management
- Wishlist (save favourite products)
- Write reviews and ratings

### 🏪 Seller Features
- Seller dashboard with product stats
- Add new products with image upload
- Edit or delete existing products
- Set price, discount %, stock quantity

### 🔧 Technical
- **Backend**: Python Flask
- **Database**: SQLite (auto-created on first run)
- **Frontend**: HTML5 + CSS3 + Bootstrap 5 + Font Awesome
- **Auth**: Session-based login with SHA-256 password hashing
- **Image Upload**: Drag & drop image uploader with preview

---

## 📁 Project Structure

```
shopkart/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── shopkart.db             # SQLite database (auto-created)
├── static/
│   ├── css/style.css       # Main stylesheet
│   ├── js/main.js          # Cart, wishlist, UI logic
│   └── uploads/            # Product images (uploaded)
└── templates/
    ├── base.html            # Base layout (navbar, footer)
    ├── index.html           # Homepage + product grid
    ├── product.html         # Product detail page
    ├── cart.html            # Shopping cart
    ├── wishlist.html        # Wishlist page
    ├── login.html           # Login page
    ├── signup.html          # Signup page (buyer or seller)
    ├── add_product.html     # Seller: add product form
    ├── edit_product.html    # Seller: edit product form
    ├── seller_dashboard.html# Seller: product management
    └── _product_card.html   # Reusable product card partial
```

---

## 🗃️ Database Schema

- **users** — id, name, email, password (hashed), role (user/seller)
- **products** — id, name, description, price, discount, category, brand, stock, rating, rating_count, image, seller_id
- **cart** — id, user_id, product_id, quantity
- **wishlist** — id, user_id, product_id (unique pair)
- **reviews** — id, user_id, product_id, rating, comment

---

## 📸 Supported Image Formats
PNG, JPG, JPEG, GIF, WEBP (max 16MB)

---

## 🛠️ Customisation Tips

- Add new categories in `add_product.html` and `base.html` category nav
- Change colour scheme via CSS variables in `style.css` (`:root` block)
- Enable email verification by integrating Flask-Mail
- Add payment gateway (Razorpay/Stripe) to the checkout flow
