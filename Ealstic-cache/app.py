from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import redis
import json

app = Flask(__name__)
CORS(app)

# =========================
# REDIS CONFIG
# =========================
redis_client = redis.Redis(
    host='my-app-redis-rwjcia.serverless.use1.cache.amazonaws.com',
    port=6379,
    ssl=True,
    decode_responses=True,
    socket_timeout=5
)

CACHE_TTL = 90

# =========================
# RDS CONFIG (PROD)
# =========================

db_write_config = {
    'host': 'app-database-1.cc3k0uecaz45.us-east-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'Password',
    'database': 'prod'
}

db_read_config = {
    'host': 'app-db-readreplica.cc3k0uecaz45.us-east-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'Password',
    'database': 'prod'
}

# =========================
# CONNECTION HELPERS
# =========================

def get_write_connection():
    print("✍️ CONNECTING TO RDS WRITER")
    return mysql.connector.connect(**db_write_config)

def get_read_connection():
    print("👀 CONNECTING TO RDS READER")
    return mysql.connector.connect(**db_read_config)

def get_db_info(cursor):
    cursor.execute("SELECT @@hostname AS host, @@read_only AS read_only")
    return cursor.fetchone()

# =========================
# ROUTES
# =========================

@app.route('/')
def index():
    return "API running with Redis + RDS (Reader/Writer) - Products Catalog"

# =========================
# READ APIs
# =========================

@app.route('/products', methods=['GET'])
def get_products():
    cache_key = "products:all"

    try:
        # 1️⃣ Redis check
        cached_data = redis_client.get(cache_key)
        if cached_data:
            print("⚡ REDIS CACHE HIT → /products")
            return jsonify({
                "data": json.loads(cached_data),
                "source": "REDIS_CACHE",
                "db_role": "READER"
            })

        print("❌ REDIS CACHE MISS → /products")

        # 2️⃣ RDS Reader
        conn = get_read_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        db_info = get_db_info(cursor)

        print(f"📖 READ FROM RDS READER → host={db_info['host']}")

        # 3️⃣ Cache result
        redis_client.setex(cache_key, CACHE_TTL, json.dumps(products, default=str))
        print("📦 DATA STORED IN REDIS CACHE")

        return jsonify({
            "data": products,
            "served_by": db_info["host"],
            "read_only": db_info["read_only"],
            "db_role": "READER",
            "source": "RDS_READER"
        })

    except Error as err:
        print("❌ ERROR:", err)
        return jsonify({'error': str(err)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    cache_key = f"product:{product_id}"

    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            print(f"⚡ REDIS CACHE HIT → /products/{product_id}")
            return jsonify({
                "data": json.loads(cached_data),
                "source": "REDIS_CACHE",
                "db_role": "READER"
            })

        print(f"❌ REDIS CACHE MISS → /products/{product_id}")

        conn = get_read_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()

        if not product:
            print("⚠️ PRODUCT NOT FOUND IN DB")
            return jsonify({'error': 'Product not found'}), 404

        db_info = get_db_info(cursor)
        print(f"📖 READ FROM RDS READER → host={db_info['host']}")

        redis_client.setex(cache_key, CACHE_TTL, json.dumps(product, default=str))
        print("📦 PRODUCT STORED IN REDIS CACHE")

        return jsonify({
            "data": product,
            "served_by": db_info["host"],
            "read_only": db_info["read_only"],
            "db_role": "READER",
            "source": "RDS_READER"
        })

    except Error as err:
        print("❌ ERROR:", err)
        return jsonify({'error': str(err)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# =========================
# WRITE APIs
# =========================

@app.route('/products/add', methods=['POST'])
def add_product():
    try:
        print("✍️ WRITE REQUEST → /products/add")
        conn = get_write_connection()
        cursor = conn.cursor()

        data = request.json
        cursor.execute(
            "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)",
            (data['name'], data['price'], data['stock'])
        )
        conn.commit()

        print("✅ WRITE SUCCESSFUL ON RDS WRITER")

        # Cache invalidation
        redis_client.delete("products:all")
        print("🧹 CACHE INVALIDATED → products:all")

        return jsonify({'message': 'Product added successfully'}), 201

    except Error as err:
        print("❌ WRITE ERROR:", err)
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/products/update/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        print(f"✍️ WRITE REQUEST → /products/update/{product_id}")
        conn = get_write_connection()
        cursor = conn.cursor()

        data = request.json
        cursor.execute(
            "UPDATE products SET name = %s, price = %s, stock = %s WHERE id = %s",
            (data['name'], data['price'], data['stock'], product_id)
        )
        conn.commit()

        print("✅ UPDATE SUCCESSFUL ON RDS WRITER")

        redis_client.delete("products:all")
        redis_client.delete(f"product:{product_id}")
        print(f"🧹 CACHE INVALIDATED → products:all, product:{product_id}")

        return jsonify({'message': 'Product updated successfully'})

    except Error as err:
        print("❌ UPDATE ERROR:", err)
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/products/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        print(f"✍️ WRITE REQUEST → /products/delete/{product_id}")
        conn = get_write_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()

        print("✅ DELETE SUCCESSFUL ON RDS WRITER")

        redis_client.delete("products:all")
        redis_client.delete(f"product:{product_id}")
        print(f"🧹 CACHE INVALIDATED → products:all, product:{product_id}")

        return jsonify({'message': 'Product deleted successfully'})

    except Error as err:
        print("❌ DELETE ERROR:", err)
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# =========================
# ENTRY POINT
# =========================
if __name__ == '__main__':
    print("🚀 Starting Flask API with Redis + RDS (Products)")
    app.run(host='0.0.0.0', port=5000, debug=True)