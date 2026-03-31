import sqlite3
import random
import os

DB_PATH = 'shopkart.db'
UPLOADS_DIR = 'static/uploads'

# Get list of existing images
if os.path.exists(UPLOADS_DIR):
    images = [f for f in os.listdir(UPLOADS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
else:
    images = ['default.jpg']

categories = ['Electronics', 'Fashion', 'Home', 'Kitchen', 'Sports', 'Books']
brands = ['TechPro', 'StyleCo', 'HomeEase', 'CookMaster', 'SportX', 'ReadMore']

def seed_products(count=100000):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Seeding {count} products...")
    
    products_to_insert = []
    
    for i in range(1, count + 1):
        category = random.choice(categories)
        brand = random.choice(brands)
        name = f"{brand} {category} Product {i}"
        description = f"This is a premium {category} product from {brand}. It's durable, high-quality and reliable for daily use."
        price = random.randint(500, 50000)
        discount = random.randint(0, 30)
        stock = random.randint(10, 500)
        rating = round(random.uniform(3.5, 5.0), 1)
        image = random.choice(images)
        seller_id = 1 # Admin seller ID
        
        products_to_insert.append((name, description, price, discount, category, image, stock, rating, seller_id))
        
        # Batch insert every 10,000 to avoid memory issues
        if len(products_to_insert) >= 10000:
            cursor.executemany('''INSERT INTO products (name, description, price, discount, category, image, stock, rating, seller_id) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', products_to_insert)
            products_to_insert = []
            print(f"Inserted {i} products...")
            
    # Insert remaining
    if products_to_insert:
        cursor.executemany('''INSERT INTO products (name, description, price, discount, category, image, stock, rating, seller_id) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', products_to_insert)
            
    conn.commit()
    conn.close()
    print("Seeding complete!")

if __name__ == "__main__":
    seed_products()
