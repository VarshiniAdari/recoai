import sqlite3
import json
import os

DB_PATH = "products.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            rating REAL,
            num_reviews INTEGER,
            category TEXT,
            brand TEXT,
            specifications TEXT,
            reviews TEXT,
            image_url TEXT,
            product_url TEXT,
            seller TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS product_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            features TEXT,
            pros TEXT,
            cons TEXT,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    conn.commit()
    conn.close()

def seed_sample_data():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM products")
    count = c.fetchone()[0]
    if count > 0:
        conn.close()
        return

    products = [
        # Smartphones
        {
            "title": "Samsung Galaxy S23 FE 5G",
            "price": 34999,
            "rating": 4.3,
            "num_reviews": 12450,
            "category": "Smartphone",
            "brand": "Samsung",
            "specifications": json.dumps({
                "RAM": "8GB",
                "Storage": "128GB",
                "Battery": "4500mAh",
                "Display": "6.4-inch AMOLED",
                "Processor": "Snapdragon 8 Gen 1",
                "Camera": "50MP Triple Camera",
                "OS": "Android 13",
                "5G": "Yes"
            }),
            "reviews": json.dumps([
                "Excellent camera performance, great for photography enthusiasts",
                "Battery life is decent but not the best in class",
                "Display is vibrant and color accurate",
                "Gaming performance is smooth with no lag",
                "Heating issues noticed during prolonged gaming sessions",
                "Premium build quality, feels great in hand",
                "Software updates are timely from Samsung"
            ]),
            "image_url": "https://images.samsung.com/is/image/samsung/p6pim/in/2307/gallery/in-galaxy-s23-fe-s711-sm-s711bzgdins-536858729",
            "product_url": "https://www.amazon.in/dp/samsung-galaxy-s23-fe",
            "seller": "Samsung India"
        },
        {
            "title": "OnePlus Nord CE 3 Lite 5G",
            "price": 17999,
            "rating": 4.1,
            "num_reviews": 8920,
            "category": "Smartphone",
            "brand": "OnePlus",
            "specifications": json.dumps({
                "RAM": "8GB",
                "Storage": "128GB",
                "Battery": "5000mAh",
                "Display": "6.72-inch LCD",
                "Processor": "Snapdragon 695",
                "Camera": "108MP Main Camera",
                "OS": "OxygenOS 13.1",
                "5G": "Yes"
            }),
            "reviews": json.dumps([
                "Great battery life, easily lasts a full day",
                "Camera quality is average in low light",
                "Performance is smooth for everyday tasks",
                "Good value for money at this price point",
                "Display is decent but not AMOLED",
                "Fast charging is a great feature",
                "Build quality could be better, feels plastic"
            ]),
            "image_url": "https://oasis.opstatics.com/content/dam/oasis/page/2023/in/nord-ce3-lite/nord-ce3-lite-pastelskyblue",
            "product_url": "https://www.amazon.in/dp/oneplus-nord-ce-3-lite",
            "seller": "OnePlus"
        },
        {
            "title": "Xiaomi Redmi Note 13 Pro 5G",
            "price": 27999,
            "rating": 4.4,
            "num_reviews": 15670,
            "category": "Smartphone",
            "brand": "Xiaomi",
            "specifications": json.dumps({
                "RAM": "8GB",
                "Storage": "256GB",
                "Battery": "5100mAh",
                "Display": "6.67-inch AMOLED 1.5K",
                "Processor": "Snapdragon 7s Gen 2",
                "Camera": "200MP Main Camera",
                "OS": "MIUI 14",
                "5G": "Yes"
            }),
            "reviews": json.dumps([
                "200MP camera is absolutely stunning for photography",
                "AMOLED display is bright and crisp",
                "Battery life is excellent, lasts 1.5 days",
                "MIUI has some bloatware pre-installed",
                "Gaming performance is excellent",
                "Build quality is premium with glass back",
                "Fast charging at 67W is very convenient"
            ]),
            "image_url": "https://i02.appmifile.com/mi-com-product/fly-birds/redmi-note-13-pro-5g",
            "product_url": "https://www.amazon.in/dp/xiaomi-redmi-note-13-pro",
            "seller": "Xiaomi India"
        },
        {
            "title": "iQOO Z7 Pro 5G",
            "price": 22999,
            "rating": 4.2,
            "num_reviews": 6340,
            "category": "Smartphone",
            "brand": "iQOO",
            "specifications": json.dumps({
                "RAM": "8GB",
                "Storage": "256GB",
                "Battery": "4600mAh",
                "Display": "6.78-inch AMOLED 120Hz",
                "Processor": "MediaTek Dimensity 7200",
                "Camera": "64MP Dual Camera",
                "OS": "FunTouch OS 13",
                "5G": "Yes"
            }),
            "reviews": json.dumps([
                "Excellent gaming performance, best in segment",
                "120Hz AMOLED display is very smooth",
                "Camera performance is good for the price",
                "Battery drains faster during gaming",
                "Build quality is premium",
                "Good for gaming and streaming",
                "Software could use improvement"
            ]),
            "image_url": "https://www.iqoo.com/in/media/iqoo-z7-pro",
            "product_url": "https://www.amazon.in/dp/iqoo-z7-pro",
            "seller": "iQOO"
        },
        {
            "title": "Realme Narzo 60 Pro 5G",
            "price": 19999,
            "rating": 4.0,
            "num_reviews": 4120,
            "category": "Smartphone",
            "brand": "Realme",
            "specifications": json.dumps({
                "RAM": "8GB",
                "Storage": "128GB",
                "Battery": "5000mAh",
                "Display": "6.7-inch ALED 120Hz",
                "Processor": "MediaTek Dimensity 7050",
                "Camera": "100MP Main Camera",
                "OS": "Realme UI 4.0",
                "5G": "Yes"
            }),
            "reviews": json.dumps([
                "Good performance for the price",
                "100MP camera takes decent photos",
                "Battery life is good",
                "Display is vibrant",
                "Occasional software glitches reported",
                "Good for students on a budget",
                "Build quality is average"
            ]),
            "image_url": "https://image.realme.com/global/img/narzo-60-pro",
            "product_url": "https://www.amazon.in/dp/realme-narzo-60-pro",
            "seller": "Realme"
        },
        # Laptops
        {
            "title": "Lenovo IdeaPad Slim 3 (2023)",
            "price": 42999,
            "rating": 4.2,
            "num_reviews": 9870,
            "category": "Laptop",
            "brand": "Lenovo",
            "specifications": json.dumps({
                "Processor": "Intel Core i5-1235U",
                "RAM": "16GB DDR4",
                "Storage": "512GB SSD",
                "Display": "15.6-inch FHD IPS",
                "Graphics": "Intel Iris Xe",
                "Battery": "45Wh",
                "OS": "Windows 11 Home",
                "Weight": "1.62kg"
            }),
            "reviews": json.dumps([
                "Great laptop for office work and productivity",
                "Battery life is impressive, lasts all day",
                "Display is bright and clear for work",
                "Keyboard is comfortable for long typing sessions",
                "Build quality could be more premium",
                "Performance is smooth for multitasking",
                "Good value for money for students"
            ]),
            "image_url": "https://p3-ofp.static.pub/fes/cms/2022/07/06/uk/ideapad-slim3",
            "product_url": "https://www.amazon.in/dp/lenovo-ideapad-slim-3",
            "seller": "Lenovo India"
        },
        {
            "title": "HP Victus 15 Gaming Laptop",
            "price": 67999,
            "rating": 4.3,
            "num_reviews": 7650,
            "category": "Laptop",
            "brand": "HP",
            "specifications": json.dumps({
                "Processor": "Intel Core i5-12450H",
                "RAM": "16GB DDR5",
                "Storage": "512GB SSD",
                "Display": "15.6-inch FHD 144Hz IPS",
                "Graphics": "NVIDIA GeForce RTX 4060",
                "Battery": "70.9Wh",
                "OS": "Windows 11 Home",
                "Weight": "2.29kg"
            }),
            "reviews": json.dumps([
                "Excellent gaming performance with RTX 4060",
                "144Hz display is smooth for gaming",
                "Battery life is poor under gaming load",
                "Runs hot under heavy load",
                "Good build quality for a gaming laptop",
                "Great for gaming and video editing",
                "Fan noise can be loud during gaming"
            ]),
            "image_url": "https://ssl-product-images.www8-hp.com/digmedialib/prodimg/knowledgebase/hp-victus-15",
            "product_url": "https://www.amazon.in/dp/hp-victus-15",
            "seller": "HP India"
        },
        {
            "title": "ASUS VivoBook 15 OLED",
            "price": 54999,
            "rating": 4.4,
            "num_reviews": 5430,
            "category": "Laptop",
            "brand": "ASUS",
            "specifications": json.dumps({
                "Processor": "Intel Core i5-12500H",
                "RAM": "16GB DDR4",
                "Storage": "512GB SSD",
                "Display": "15.6-inch FHD OLED",
                "Graphics": "NVIDIA GeForce RTX 2050",
                "Battery": "70Wh",
                "OS": "Windows 11 Home",
                "Weight": "1.8kg"
            }),
            "reviews": json.dumps([
                "OLED display is stunning, best in class",
                "Great for content creation and photo editing",
                "Performance is smooth for most tasks",
                "Battery life is average",
                "Premium build quality, looks beautiful",
                "Good for students and professionals",
                "Keyboard backlight is a nice touch"
            ]),
            "image_url": "https://www.asus.com/media/global/products/vivobook-15-oled",
            "product_url": "https://www.amazon.in/dp/asus-vivobook-15-oled",
            "seller": "ASUS India"
        },
        # Headphones
        {
            "title": "Sony WH-1000XM5 Wireless Headphones",
            "price": 24999,
            "rating": 4.6,
            "num_reviews": 18920,
            "category": "Headphones",
            "brand": "Sony",
            "specifications": json.dumps({
                "Type": "Over-ear",
                "Connectivity": "Bluetooth 5.2",
                "ANC": "Industry-leading ANC",
                "Battery": "30 hours playback",
                "Quick Charge": "3 min = 3 hours",
                "Driver": "30mm",
                "Foldable": "No",
                "Weight": "250g"
            }),
            "reviews": json.dumps([
                "Best ANC headphones in the market",
                "Sound quality is exceptional and balanced",
                "Very comfortable for long listening sessions",
                "Call quality is excellent with multipoint connection",
                "Not foldable which reduces portability",
                "Battery life is outstanding",
                "Premium build quality with soft cushions"
            ]),
            "image_url": "https://www.sony.co.in/image/wh1000xm5",
            "product_url": "https://www.amazon.in/dp/sony-wh-1000xm5",
            "seller": "Sony India"
        },
        {
            "title": "boAt Rockerz 550 Bluetooth Headphones",
            "price": 1499,
            "rating": 3.9,
            "num_reviews": 45670,
            "category": "Headphones",
            "brand": "boAt",
            "specifications": json.dumps({
                "Type": "Over-ear",
                "Connectivity": "Bluetooth 5.0",
                "ANC": "No",
                "Battery": "20 hours playback",
                "Quick Charge": "No",
                "Driver": "40mm",
                "Foldable": "Yes",
                "Weight": "220g"
            }),
            "reviews": json.dumps([
                "Great value for money at this price",
                "Bass is heavy and punchy",
                "Comfortable for casual listening",
                "Build quality is plastic but decent",
                "No ANC so background noise is audible",
                "Good for casual listeners and students",
                "Microphone quality is average"
            ]),
            "image_url": "https://www.boat-lifestyle.com/cdn/shop/products/rockerz-550",
            "product_url": "https://www.amazon.in/dp/boat-rockerz-550",
            "seller": "Imagine Marketing"
        },
        {
            "title": "JBL Tune 770NC Wireless Headphones",
            "price": 7999,
            "rating": 4.2,
            "num_reviews": 6780,
            "category": "Headphones",
            "brand": "JBL",
            "specifications": json.dumps({
                "Type": "Over-ear",
                "Connectivity": "Bluetooth 5.3",
                "ANC": "Adaptive ANC",
                "Battery": "70 hours playback",
                "Quick Charge": "10 min = 2 hours",
                "Driver": "40mm",
                "Foldable": "Yes",
                "Weight": "218g"
            }),
            "reviews": json.dumps([
                "Excellent battery life at 70 hours",
                "ANC is effective for the price",
                "JBL Pure Bass sound signature",
                "Comfortable and lightweight",
                "Good value mid-range headphones",
                "Call quality is decent",
                "Foldable design makes it portable"
            ]),
            "image_url": "https://in.jbl.com/dw/image/v2/BFND_PRD/on/demandware.static/jbl-tune-770nc",
            "product_url": "https://www.amazon.in/dp/jbl-tune-770nc",
            "seller": "Harman India"
        },
        {
            "title": "Apple AirPods Pro (2nd Gen)",
            "price": 24900,
            "rating": 4.5,
            "num_reviews": 22340,
            "category": "Headphones",
            "brand": "Apple",
            "specifications": json.dumps({
                "Type": "In-ear (TWS)",
                "Connectivity": "Bluetooth 5.3",
                "ANC": "Adaptive Transparency + ANC",
                "Battery": "6 hours (30 with case)",
                "Quick Charge": "Yes",
                "Driver": "Custom Apple driver",
                "Foldable": "N/A (TWS)",
                "Weight": "5.3g per bud"
            }),
            "reviews": json.dumps([
                "Best ANC for in-ear form factor",
                "Seamless integration with Apple ecosystem",
                "Spatial audio is immersive",
                "Expensive compared to Android alternatives",
                "Excellent fit with multiple ear tip sizes",
                "Great for iPhone users",
                "Call quality is crystal clear"
            ]),
            "image_url": "https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/MQD83",
            "product_url": "https://www.amazon.in/dp/apple-airpods-pro-2nd-gen",
            "seller": "Apple India"
        },
        {
            "title": "Sennheiser Momentum 4 Wireless",
            "price": 22990,
            "rating": 4.5,
            "num_reviews": 3450,
            "category": "Headphones",
            "brand": "Sennheiser",
            "specifications": json.dumps({
                "Type": "Over-ear",
                "Connectivity": "Bluetooth 5.2",
                "ANC": "Adaptive ANC",
                "Battery": "60 hours playback",
                "Quick Charge": "Yes",
                "Driver": "42mm",
                "Foldable": "Yes",
                "Weight": "293g"
            }),
            "reviews": json.dumps([
                "Audiophile-grade sound quality",
                "60-hour battery life is exceptional",
                "Very comfortable padded earcups",
                "ANC is good but not best-in-class",
                "Premium build quality worth the price",
                "Neutral and balanced sound signature",
                "Great for music enthusiasts and audiophiles"
            ]),
            "image_url": "https://assets.sennheiser.com/img/momentum4-wireless",
            "product_url": "https://www.amazon.in/dp/sennheiser-momentum-4",
            "seller": "Sennheiser India"
        }
    ]

    for p in products:
        c.execute('''
            INSERT INTO products (title, price, rating, num_reviews, category, brand, specifications, reviews, image_url, product_url, seller)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (p["title"], p["price"], p["rating"], p["num_reviews"], p["category"],
              p["brand"], p["specifications"], p["reviews"], p["image_url"], p["product_url"], p["seller"]))

    conn.commit()
    conn.close()

def get_products_by_category(category):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE LOWER(category) = LOWER(?)", (category,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_products():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_product_features(product_id, features, pros, cons):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM product_features WHERE product_id=?", (product_id,))
    existing = c.fetchone()
    if existing:
        c.execute("UPDATE product_features SET features=?, pros=?, cons=? WHERE product_id=?",
                  (json.dumps(features), json.dumps(pros), json.dumps(cons), product_id))
    else:
        c.execute("INSERT INTO product_features (product_id, features, pros, cons) VALUES (?, ?, ?, ?)",
                  (product_id, json.dumps(features), json.dumps(pros), json.dumps(cons)))
    conn.commit()
    conn.close()

def get_product_features(product_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM product_features WHERE product_id=?", (product_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None
