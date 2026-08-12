from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
import boto3
from botocore.exceptions import ClientError
import json

app = Flask(__name__)
CORS(app)

# 🔹 Get secret from AWS Secrets Manager
def get_secret():
    secret_name = "rds!db-d4fb4117-fa17-4d37-b5a0-27fc823399c1"
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client("secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)   # returns dict with username + password


# 🔹 Database Configuration (pointing to prod DB)
db_secret = get_secret()
db_config = {
    'host': 'database-2-public-rds-secret-manager.cynsuiygc95m.us-east-1.rds.amazonaws.com',
    'user': db_secret['username'],      # from secret
    'password': db_secret['password'],  # from secret
    'database': 'prod'                  # ✅ changed to prod
}


# 🔹 Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(**db_config)


# 1️⃣ Get all products
@app.route('/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(products)


# 2️⃣ Get product by ID
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    if product:
        return jsonify(product)
    return jsonify({'error': 'Product not found'}), 404


# 3️⃣ Add a new product
@app.route('/products/add', methods=['POST'])
def add_product():
    data = request.json
    name = data.get('name')
    price = data.get('price')
    stock = data.get('stock')
    if not name or price is None or stock is None:
        return jsonify({'error': 'Name, Price, and Stock are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)", (name, price, stock))
        conn.commit()
        return jsonify({'message': 'Product added successfully'}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()


# 4️⃣ Update product by ID
@app.route('/products/update/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    name = data.get('name')
    price = data.get('price')
    stock = data.get('stock')
    if not name or price is None or stock is None:
        return jsonify({'error': 'Name, Price, and Stock are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    if not cursor.fetchone():
        return jsonify({'error': 'Product not found'}), 404

    try:
        cursor.execute("UPDATE products SET name = %s, price = %s, stock = %s WHERE id = %s", (name, price, stock, product_id))
        conn.commit()
        return jsonify({'message': 'Product updated successfully'})
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()


# 5️⃣ Delete product by ID
@app.route('/products/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    if not cursor.fetchone():
        return jsonify({'error': 'Product not found'}), 404

    try:
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
        return jsonify({'message': 'Product deleted successfully'})
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()


# 🔹 Root route
@app.route('/')
def index():
    return "Product API is running on prod DB!"


# Entry Point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)