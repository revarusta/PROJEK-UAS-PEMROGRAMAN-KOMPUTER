from flask import Flask, request, jsonify, render_template  # type: ignore
import mysql.connector  # type: ignore
from mysql.connector import errorcode  # type: ignore

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # kosongkan jika password XAMPP kosong
    "database": "jual_makeup"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        conn.database = DB_CONFIG['database']
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produk (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price INT NOT NULL
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Database dan tabel 'produk' siap digunakan.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Username atau password salah.")
        else:
            print(f"Error: {err}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produk")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(products)

@app.route('/api/add-product', methods=['POST'])
def add_product():
    data = request.json
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({"error": "Data harus memiliki 'name' dan 'price'"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produk (name, price) VALUES (%s, %s)", (data['name'], data['price']))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "1 produk berhasil ditambahkan", "produk": data})

@app.route('/api/add-products', methods=['POST'])
def add_multiple_products():
    products = request.json
    if not isinstance(products, list):
        return jsonify({"error": "Data harus berupa list produk"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    for item in products:
        if 'name' not in item or 'price' not in item:
            cursor.close()
            conn.close()
            return jsonify({"error": "Setiap produk harus memiliki 'name' dan 'price'"}), 400
        cursor.execute("INSERT INTO produk (name, price) VALUES (%s, %s)", (item['name'], item['price']))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": f"{len(products)} produk berhasil ditambahkan."})

# ✅ GET produk berdasarkan ID
@app.route('/api/product/<int:id>', methods=['GET'])
def get_product_by_id(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produk WHERE id = %s", (id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()

    if product:
        return jsonify(product)
    else:
        return jsonify({"error": "Produk tidak ditemukan"}), 404

# ✅ UPDATE produk berdasarkan ID
@app.route('/api/update-product/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.json
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({"error": "Data harus memiliki 'name' dan 'price'"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE produk SET name = %s, price = %s WHERE id = %s",
                   (data['name'], data['price'], id))
    conn.commit()
    affected_rows = cursor.rowcount
    cursor.close()
    conn.close()

    if affected_rows == 0:
        return jsonify({"error": "Produk tidak ditemukan"}), 404

    return jsonify({"message": f"Produk dengan id {id} berhasil diupdate"})

# ✅ DELETE produk berdasarkan ID
@app.route('/api/delete-product/<int:id>', methods=['DELETE'])
def delete_product(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produk WHERE id = %s", (id,))
    conn.commit()
    affected_rows = cursor.rowcount
    cursor.close()
    conn.close()

    if affected_rows == 0:
        return jsonify({"error": "Produk tidak ditemukan"}), 404

    return jsonify({"message": f"Produk dengan id {id} berhasil dihapus"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)