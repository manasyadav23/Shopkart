from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
import os
import hashlib
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'shopkart_secret_key_2024'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

DB_PATH = os.path.join(BASE_DIR, 'shopkart.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        discount INTEGER DEFAULT 0,
        category TEXT,
        brand TEXT,
        stock INTEGER DEFAULT 0,
        rating REAL DEFAULT 0,
        rating_count INTEGER DEFAULT 0,
        image TEXT,
        seller_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (seller_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        UNIQUE(user_id, product_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        rating INTEGER,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        payment_method TEXT DEFAULT 'Cash on Delivery',
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )''')
    # Seed demo data
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        admin_pw = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                  ('Admin', 'admin@shopkart.com', admin_pw, 'seller'))
        user_pw = hashlib.sha256('user123'.encode()).hexdigest()
        c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                  ('Demo User', 'user@shopkart.com', user_pw, 'user'))
        demo_products = [
            ('Apple iPhone 15 Pro', 'The latest iPhone with titanium design, A17 Pro chip, and a 48MP camera system.', 134900, 10, 'Electronics', 'Apple', 45, 4.8, 2341, 'iphone15.jpg'),
            ('Samsung Galaxy S24 Ultra', 'Flagship Android phone with built-in S Pen, 200MP camera, and Snapdragon 8 Gen 3.', 124999, 15, 'Electronics', 'Samsung', 30, 4.7, 1876, 'samsung.jpg'),
            ('Sony WH-1000XM5', 'Industry-leading noise cancelling headphones with 30-hour battery life.', 29990, 20, 'Electronics', 'Sony', 120, 4.9, 4521, 'sony.jpg'),
            ('Nike Air Max 270', 'Lifestyle shoes with Max Air unit and breathable mesh upper for all-day comfort.', 11995, 30, 'Footwear', 'Nike', 200, 4.5, 987, 'nike.jpg'),
            ('Levi\'s 511 Slim Jeans', 'Classic slim-fit jeans in authentic denim with modern stretch fabric.', 3999, 25, 'Clothing', 'Levi\'s', 350, 4.3, 2109, 'levis.jpg'),
            ('Instant Pot Duo 7-in-1', 'Multi-use pressure cooker, slow cooker, rice cooker, steamer, and more.', 8999, 35, 'Kitchen', 'Instant Pot', 80, 4.7, 3456, 'instantpot.jpg'),
            ('The Alchemist', 'Paulo Coelho\'s masterpiece about following your dreams and finding your destiny.', 299, 5, 'Books', 'HarperCollins', 500, 4.6, 8765, 'alchemist.jpg'),
            ('Dyson V15 Detect', 'Most powerful cordless vacuum with laser dust detection and LCD screen.', 52900, 8, 'Appliances', 'Dyson', 25, 4.8, 654, 'dyson.jpg'),
            ('MacBook Pro 16', 'M3 Max chip, 36GB RAM, 1TB SSD. The ultimate pro laptop.', 249900, 5, 'Electronics', 'Apple', 20, 4.9, 1205, 'macbook.jpg'),
            ('iPad Pro', '12.9-inch Liquid Retina XDR display, M2 chip.', 112900, 8, 'Electronics', 'Apple', 60, 4.8, 3400, 'ipad.jpg'),
            ('Apple Watch Ultra 2', 'Rugged titanium case, bright display, precision GPS.', 89900, 5, 'Electronics', 'Apple', 40, 4.7, 890, 'watch.jpg'),
            ('AirPods Pro 2', 'Active Noise Cancellation, Adaptive Audio, USB-C.', 24900, 10, 'Electronics', 'Apple', 150, 4.8, 5600, 'airpods.jpg'),
            ('Kindle Paperwhite', '6.8-inch display, adjustable warm light, waterproof.', 13999, 15, 'Electronics', 'Amazon', 300, 4.8, 12400, 'kindle.jpg'),
            ('Echo Dot (5th Gen)', 'Smart speaker with Alexa and deep bass.', 4499, 40, 'Electronics', 'Amazon', 500, 4.6, 23000, 'echo.jpg'),
            ('PlayStation 5', 'Ultra-high speed SSD, ray tracing, 4K-TV gaming.', 49990, 0, 'Gaming', 'Sony', 15, 4.9, 8900, 'ps5.jpg'),
            ('Xbox Series X', 'Fastest, most powerful Xbox ever. 4K gaming.', 49990, 5, 'Gaming', 'Microsoft', 25, 4.8, 4500, 'xbox.jpg'),
            ('Nintendo Switch OLED', '7-inch OLED screen, 64GB storage, enhanced audio.', 34990, 8, 'Gaming', 'Nintendo', 80, 4.8, 6700, 'switch.jpg'),
            ('Dell XPS 15', '13th Gen Intel Core i7, RTX 4050, OLED display.', 189900, 12, 'Electronics', 'Dell', 10, 4.6, 450, 'dell.jpg'),
            ('ASUS ROG Zephyrus G14', 'AMD Ryzen 9, RTX 4060, AniMe Matrix display.', 149990, 15, 'Electronics', 'ASUS', 20, 4.7, 670, 'asus.jpg'),
            ('Bose QuietComfort Ultra', 'World-class noise cancellation, spatial audio.', 35900, 10, 'Electronics', 'Bose', 50, 4.8, 1200, 'bose.jpg'),
            ('JBL Charge 5', 'Portable Bluetooth speaker with waterproof design.', 12999, 20, 'Electronics', 'JBL', 100, 4.7, 4500, 'jbl.jpg'),
            ('GoPro HERO12 Black', 'Waterproof action camera with 5.3K60 video.', 39990, 10, 'Cameras', 'GoPro', 40, 4.7, 980, 'gopro.jpg'),
            ('Canon EOS R5', 'Mirrorless camera with 45MP full-frame sensor.', 339990, 5, 'Cameras', 'Canon', 5, 4.9, 150, 'canon.jpg'),
            ('Nikon Z9', 'Flagship mirrorless camera, 8K video.', 469990, 0, 'Cameras', 'Nikon', 3, 4.9, 80, 'nikon.jpg'),
            ('LG C3 OLED TV 65"', '4K Smart TV with evo panel and a9 Gen6 AI Processor.', 169990, 25, 'Appliances', 'LG', 15, 4.8, 890, 'lg.jpg'),
            ('Breville Barista Express', 'Espresso machine with built-in grinder.', 69999, 15, 'Kitchen', 'Breville', 25, 4.7, 1200, 'coffee.jpg'),
            ('Vitamix E310', 'Explorian blender, professional-grade.', 39999, 20, 'Kitchen', 'Vitamix', 35, 4.8, 800, 'blender.jpg'),
            ('Adidas Ultraboost 1.0', 'Running shoes with Boost midsole for energy return.', 15999, 30, 'Footwear', 'Adidas', 150, 4.6, 2100, 'sneakers.jpg'),
            ('The North Face McMurdo', 'Men\'s waterproof core parka down jacket.', 24999, 10, 'Clothing', 'The North Face', 40, 4.8, 450, 'jacket.jpg'),
            ('Samsonite Omni PC', 'Hardside expandable luggage with spinner wheels.', 12999, 25, 'Travel', 'Samsonite', 80, 4.7, 3400, 'bag.jpg'),
            ('Chanel No. 5', 'Classic eau de parfum, 100ml.', 15990, 0, 'Beauty', 'Chanel', 20, 4.9, 560, 'perfume.jpg'),
            ('Rolex Submariner Date', 'Oystersteel, 41mm case, rotatable bezel.', 850000, 0, 'Watches', 'Rolex', 2, 4.9, 45, 'watch2.jpg')
        ]
        for p in demo_products:
            c.execute('''INSERT INTO products (name, description, price, discount, category, brand, stock, rating, rating_count, image, seller_id)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)''', p)
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def get_cart_count():
    if 'user_id' not in session:
        return 0
    conn = get_db()
    count = conn.execute("SELECT SUM(quantity) FROM cart WHERE user_id=?", (session['user_id'],)).fetchone()[0]
    conn.close()
    return count or 0

def get_wishlist_ids():
    if 'user_id' not in session:
        return []
    conn = get_db()
    rows = conn.execute("SELECT product_id FROM wishlist WHERE user_id=?", (session['user_id'],)).fetchall()
    conn.close()
    return [r['product_id'] for r in rows]

# ── Routes ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    conn = get_db()
    search = request.args.get('q', '')
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    sort = request.args.get('sort', '')

    query = "SELECT * FROM products WHERE 1=1"
    params = [] # type: list
    if search:
        query += " AND (name LIKE ? OR brand LIKE ? OR description LIKE ?)"
        params += [f'%{search}%', f'%{search}%', f'%{search}%']
    if category:
        query += " AND category=?"
        params.append(category)
    if min_price:
        query += " AND (price - price*discount/100) >= ?"
        params.append(str(min_price))
    if max_price:
        query += " AND (price - price*discount/100) <= ?"
        params.append(str(max_price))

    # Pagination
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    # Get total count for pagination
    count_query = "SELECT COUNT(*) FROM products WHERE 1=1"
    count_params = [] # Use a separate params list for count query
    if search:
        count_query += " AND (name LIKE ? OR brand LIKE ? OR description LIKE ?)"
        count_params += [f'%{search}%', f'%{search}%', f'%{search}%']
    if category:
        count_query += " AND category=?"
        count_params.append(category)
    if min_price:
        count_query += " AND (price - price*discount/100) >= ?"
        count_params.append(str(min_price))
    if max_price:
        count_query += " AND (price - price*discount/100) <= ?"
        count_params.append(str(max_price))
    
    total_products = conn.execute(count_query, count_params).fetchone()[0]
    total_pages = (total_products + per_page - 1) // per_page

    if sort == 'price_asc':
        query += " ORDER BY (price - price*discount/100) ASC"
    elif sort == 'price_desc':
        query += " ORDER BY (price - price*discount/100) DESC"
    elif sort == 'rating':
        query += " ORDER BY rating DESC"
    elif sort == 'newest':
        query += " ORDER BY created_at DESC"
    else:
        query += " ORDER BY id DESC"

    # Add LIMIT and OFFSET to the main query
    query += " LIMIT ? OFFSET ?"
    params += [per_page, offset]

    products = conn.execute(query, params).fetchall()
    categories = conn.execute("SELECT DISTINCT category FROM products").fetchall()
    featured = conn.execute("SELECT * FROM products ORDER BY rating DESC LIMIT 4").fetchall()
    conn.close()
    wishlist_ids = get_wishlist_ids()
    return render_template('index.html', products=products, categories=categories,
                           featured=featured, search=search, category=category,
                           min_price=min_price, max_price=max_price, sort=sort,
                           page=page, total_pages=total_pages,
                           cart_count=get_cart_count(), wishlist_ids=wishlist_ids)

@app.route('/product/<int:pid>')
def product_detail(pid):
    conn = get_db()
    product = conn.execute("SELECT p.*, u.name as seller_name FROM products p LEFT JOIN users u ON p.seller_id=u.id WHERE p.id=?", (pid,)).fetchone()
    if not product:
        return redirect(url_for('index'))
    related = conn.execute("SELECT * FROM products WHERE category=? AND id!=? LIMIT 4", (product['category'], pid)).fetchall()
    reviews = conn.execute("SELECT r.*, u.name FROM reviews r JOIN users u ON r.user_id=u.id WHERE r.product_id=? ORDER BY r.created_at DESC", (pid,)).fetchall()
    conn.close()
    wishlist_ids = get_wishlist_ids()
    return render_template('product.html', product=product, related=related,
                           reviews=reviews, cart_count=get_cart_count(), wishlist_ids=wishlist_ids)

@app.route('/seller/add', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session or session.get('role') != 'seller':
        flash('Please login as a seller to add products.', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        discount = int(request.form.get('discount', 0))
        category = request.form['category']
        brand = request.form['brand']
        stock = int(request.form['stock'])
        rating = float(request.form.get('rating', 0))
        image_filename = 'default.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                image_filename = f"{uuid.uuid4().hex}.{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        conn = get_db()
        conn.execute('''INSERT INTO products (name, description, price, discount, category, brand, stock, rating, image, seller_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (name, description, price, discount, category, brand, stock, rating, image_filename, session['user_id']))
        conn.commit()
        conn.close()
        flash('Product added successfully!', 'success')
        return redirect(url_for('seller_dashboard'))
    conn = get_db()
    categories = conn.execute("SELECT DISTINCT category FROM products").fetchall()
    conn.close()
    return render_template('add_product.html', categories=categories, cart_count=get_cart_count())

@app.route('/seller/dashboard')
def seller_dashboard():
    if 'user_id' not in session or session.get('role') != 'seller':
        return redirect(url_for('login'))
    conn = get_db()
    products = conn.execute("SELECT * FROM products WHERE seller_id=? ORDER BY created_at DESC", (session['user_id'],)).fetchall()
    stats = conn.execute("SELECT COUNT(*) as count, SUM(price) as revenue FROM products WHERE seller_id=?", (session['user_id'],)).fetchone()
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    return render_template('seller_dashboard.html', products=products, stats=stats, user_count=user_count, cart_count=get_cart_count())

@app.route('/seller/edit/<int:pid>', methods=['GET', 'POST'])
def edit_product(pid):
    if 'user_id' not in session or session.get('role') != 'seller':
        return redirect(url_for('login'))
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE id=? AND seller_id=?", (pid, session['user_id'])).fetchone()
    if not product:
        conn.close()
        return redirect(url_for('seller_dashboard'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        discount = int(request.form.get('discount', 0))
        category = request.form['category']
        brand = request.form['brand']
        stock = int(request.form['stock'])
        rating = float(request.form.get('rating', 0))
        image_filename = product['image']
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                image_filename = f"{uuid.uuid4().hex}.{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        conn.execute('''UPDATE products SET name=?, description=?, price=?, discount=?, category=?, brand=?, stock=?, rating=?, image=?
                        WHERE id=? AND seller_id=?''',
                     (name, description, price, discount, category, brand, stock, rating, image_filename, pid, session['user_id']))
        conn.commit()
        conn.close()
        flash('Product updated!', 'success')
        return redirect(url_for('seller_dashboard'))
    categories = conn.execute("SELECT DISTINCT category FROM products").fetchall()
    conn.close()
    return render_template('edit_product.html', product=product, categories=categories, cart_count=get_cart_count())

@app.route('/seller/delete/<int:pid>', methods=['POST'])
def delete_product(pid):
    if 'user_id' not in session or session.get('role') != 'seller':
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute("DELETE FROM products WHERE id=? AND seller_id=?", (pid, session['user_id']))
    conn.commit()
    conn.close()
    flash('Product deleted.', 'success')
    return redirect(url_for('seller_dashboard'))

# ── Auth ─────────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = user['role']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html', cart_count=0)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = hash_password(request.form['password'])
        role = request.form.get('role', 'user')
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)", (name, email, password, role))
            conn.commit()
            user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = user['role']
            conn.close()
            flash('Account created successfully!', 'success')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            conn.close()
            flash('Email already registered.', 'error')
    return render_template('signup.html', cart_count=0)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ── Cart ─────────────────────────────────────────────────────────────────────

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    items = conn.execute('''SELECT c.id, c.quantity, p.* FROM cart c
                            JOIN products p ON c.product_id=p.id
                            WHERE c.user_id=?''', (session['user_id'],)).fetchall()
    conn.close()
    total = sum((i['price'] * (1 - i['discount']/100)) * i['quantity'] for i in items)
    return render_template('cart.html', items=items, total=total, cart_count=get_cart_count())

@app.route('/cart/add/<int:pid>', methods=['POST'])
def add_to_cart(pid):
    if 'user_id' not in session:
        return jsonify({'success': False, 'redirect': url_for('login')})
    qty = int(request.form.get('quantity', 1))
    conn = get_db()
    existing = conn.execute("SELECT * FROM cart WHERE user_id=? AND product_id=?", (session['user_id'], pid)).fetchone()
    if existing:
        conn.execute("UPDATE cart SET quantity=quantity+? WHERE user_id=? AND product_id=?", (qty, session['user_id'], pid))
    else:
        conn.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)", (session['user_id'], pid, qty))
    conn.commit()
    count = conn.execute("SELECT SUM(quantity) FROM cart WHERE user_id=?", (session['user_id'],)).fetchone()[0]
    conn.close()
    return jsonify({'success': True, 'cart_count': count or 0})

@app.route('/cart/remove/<int:cid>', methods=['POST'])
def remove_from_cart(cid):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute("DELETE FROM cart WHERE id=? AND user_id=?", (cid, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('cart'))

@app.route('/cart/update/<int:cid>', methods=['POST'])
def update_cart(cid):
    qty = int(request.form.get('quantity', 1))
    conn = get_db()
    if qty <= 0:
        conn.execute("DELETE FROM cart WHERE id=?", (cid,))
    else:
        conn.execute("UPDATE cart SET quantity=? WHERE id=?", (qty, cid))
    conn.commit()
    conn.close()
    return redirect(url_for('cart'))

# ── Wishlist ──────────────────────────────────────────────────────────────────

@app.route('/wishlist/toggle/<int:pid>', methods=['POST'])
def toggle_wishlist(pid):
    if 'user_id' not in session:
        return jsonify({'success': False, 'redirect': url_for('login')})
    conn = get_db()
    existing = conn.execute("SELECT * FROM wishlist WHERE user_id=? AND product_id=?", (session['user_id'], pid)).fetchone()
    if existing:
        conn.execute("DELETE FROM wishlist WHERE user_id=? AND product_id=?", (session['user_id'], pid))
        added = False
    else:
        conn.execute("INSERT OR IGNORE INTO wishlist (user_id, product_id) VALUES (?, ?)", (session['user_id'], pid))
        added = True
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'added': added})

@app.route('/wishlist')
def wishlist():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    items = conn.execute('''SELECT p.* FROM wishlist w JOIN products p ON w.product_id=p.id
                            WHERE w.user_id=?''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('wishlist.html', items=items, cart_count=get_cart_count(), wishlist_ids=[i['id'] for i in items])

# ── Review ────────────────────────────────────────────────────────────────────

@app.route('/review/add/<int:pid>', methods=['POST'])
def add_review(pid):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    rating = int(request.form['rating'])
    comment = request.form['comment']
    conn = get_db()
    conn.execute("INSERT INTO reviews (user_id, product_id, rating, comment) VALUES (?, ?, ?, ?)",
                 (session['user_id'], pid, rating, comment))
    avg = conn.execute("SELECT AVG(rating), COUNT(*) FROM reviews WHERE product_id=?", (pid,)).fetchone()
    conn.execute("UPDATE products SET rating=?, rating_count=? WHERE id=?", (round(avg[0], 1), avg[1], pid))
    conn.commit()
    conn.close()
    return redirect(url_for('product_detail', pid=pid))

# ── Checkout ──────────────────────────────────────────────────────────────────

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    items = conn.execute('''SELECT c.id, c.quantity, p.* FROM cart c
                            JOIN products p ON c.product_id=p.id
                            WHERE c.user_id=?''', (session['user_id'],)).fetchall()
    
    if not items:
        conn.close()
        return redirect(url_for('cart'))
        
    total = sum((i['price'] * (1 - i['discount']/100)) * i['quantity'] for i in items)
    
    if request.method == 'POST':
        payment_method = request.form.get('payment', 'Cash on Delivery')
        # Create order record
        c = conn.cursor()
        c.execute("INSERT INTO orders (user_id, total_amount, payment_method) VALUES (?, ?, ?)", 
                  (session['user_id'], total, payment_method))
        order_id = c.lastrowid
        
        # Save order items
        for item in items:
            product_id = item['id'] # p.id from the join
            price = item['price'] * (1 - item['discount']/100)
            c.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                      (order_id, product_id, item['quantity'], price))
                      
        # Clear cart
        c.execute("DELETE FROM cart WHERE user_id=?", (session['user_id'],))
        conn.commit()
        conn.close()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('order_success'))
        
    conn.close()
    return render_template('checkout.html', items=items, total=total, cart_count=0)

@app.route('/order-success')
def order_success():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('order_success.html', cart_count=get_cart_count())

@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    
    # Get all orders for the user
    user_orders = conn.execute("SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC", (session['user_id'],)).fetchall()
    
    # For each order, get its items
    orders_list = []
    for order in user_orders:
        items = conn.execute('''SELECT oi.*, p.name, p.image, p.brand FROM order_items oi 
                                JOIN products p ON oi.product_id = p.id 
                                WHERE oi.order_id=?''', (order['id'],)).fetchall()
        orders_list.append({
            'info': order,
            'order_items': items
        })
    
    conn.close()
    return render_template('orders.html', all_orders=orders_list, cart_count=get_cart_count())

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template('profile.html', user=user, cart_count=get_cart_count())

@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        try:
            conn.execute("UPDATE users SET name=?, email=? WHERE id=?", (name, email, session['user_id']))
            conn.commit()
            session['user_name'] = name
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        except sqlite3.IntegrityError:
            flash('Email already in use.', 'error')
    
    user = conn.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template('edit_profile.html', user=user, cart_count=get_cart_count())

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    init_db()
    app.run(debug=True, port=5000)
