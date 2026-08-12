# Product Catalog Management System (AWS + Flask + Redis + MySQL)

A secure, high-performance web application designed to demonstrate a cloud-native architecture using **AWS (RDS Read/Write Split, ElastiCache Redis)**, a **Flask backend**, and a responsive **HTML/JavaScript frontend**. 

---

## 🏗️ Architecture Overview

1. **Frontend**: HTML5, CSS3 (Segoe UI Dashboard), and vanilla JavaScript communicating with the backend via REST APIs.
2. **Backend API**: Python Flask framework supporting CORS, MySQL connector, and Redis caching.
3. **Caching Layer**: Amazon ElastiCache (Serverless Redis) used to cache product catalog data (TTL: 90 seconds) to reduce read strain on the database.
4. **Database Layer**: Amazon RDS MySQL with a **Read/Write Split**:
   - **Writer Instance**: Handles all `POST`, `PUT`, and `DELETE` requests and manages cache invalidation.
   - **Reader Instance**: Handles high-throughput `GET` requests to optimize query load.

---

## 🗄️ Database Schema & Seeding

Run the following SQL commands in your MySQL/RDS `prod` database to set up the product table and seed initial data:

```sql
-- 1. Create the database
CREATE DATABASE IF NOT EXISTS prod;

-- 2. Select the database
USE prod;

-- 3. Create the products table matching your Python app
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL
);

-- 4. Seed initial products
INSERT INTO products (name, price, stock) VALUES 
('Raspberry Pi 5 Starter Kit', 120.00, 25),
('Ergonomic Vertical Mouse', 29.99, 80),
('Cloud Architect Exam Voucher', 150.00, 500),
('Studio Condenser Microphone', 199.50, 40),
('Mechanical Switch Tester', 15.00, 150);

 Commit;
``` 

Project File Structure
Plaintext
project_root/
│
├── app.py                  # Main Flask application (Read/Write split & Redis caching)
├── templates/
│   └── index.html          # Frontend dashboard UI
└── README.md               # Project documentation


🚀 Local Installation & Setup
1. PrerequisitesPython 3.9 or higher acess to AWS RDS MySQL (Writer & Reader endpoints) and Amazon ElastiCache Redis.
2. Install DependenciesRun the following commands in your terminal to install the necessary Python packages:Bashpip install flask flask-cors mysql-connector-python redis
3. Configure Endpoints in app.pyEnsure your configuration blocks match your live AWS environment hostnames:Python# Redis Config
redis_client = redis.Redis(
    host='YOUR_REDIS_ENDPOINT_HERE',
    port=6379,
    ssl=True,
    decode_responses=True,
    socket_timeout=5
)

# RDS Writer Config
db_write_config = {
    'host': 'YOUR_RDS_WRITER_ENDPOINT_HERE',
    'user': 'admin',
    'password': 'YOUR_PASSWORD',
    'database': 'prod'
}

# RDS Reader Config
db_read_config = {
    'host': 'YOUR_RDS_READER_ENDPOINT_HERE',
    'user': 'admin',
    'password': 'YOUR_PASSWORD',
    'database': 'prod'
}
4. Run the ApplicationStart your Flask server: python app.py

Behavior
- On first run the script queries RDS and stores the result in Redis with a TTL (default 90s).
- Subsequent runs (within TTL) will return results from Redis cache.
- After the TTL expires, the next run will reload data from RDS and refresh the cache.

Notes
- Ensure your EC2 security group can reach RDS on port 3306 and ElastiCache on port 6379.
- For production, use IAM, parameter stores, or secret managers for secrets.


curl -X GET http://localhost:5000/products

# Add a new product
curl -X POST http://localhost:5000/products/add \
  -H "Content-Type: application/json" \
  -d '{"name":"Wireless Mechanical Keyboard","price":89.99,"stock":45}'

# Update an existing product
curl -X PUT http://localhost:5000/products/update/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Raspberry Pi 5 Pro","price":135.00,"stock":20}'

# Delete a product
curl -X DELETE http://localhost:5000/products/delete/1
