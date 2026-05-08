from flask import Flask, render_template, request, jsonify, send_from_directory, session
import os
import pandas as pd
import mysql.connector
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='.')
app.secret_key = "replace_this_with_a_strong_secret"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXT = {"png", "jpg", "jpeg", "bmp"}

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Pratiksha@2006",
        database="Farm",
        charset="utf8mb4"
    )

DATASET_CSV = "sugarcane_dataset.csv"
df_dataset = pd.read_csv(DATASET_CSV)
df_dataset.columns = df_dataset.columns.str.strip()
df_dataset["image_name"] = df_dataset["image_path"].apply(lambda x: os.path.basename(str(x)).strip().lower())

def get_request_value(key, default=None):
    if request.is_json:
        return request.get_json().get(key, default)
    return request.form.get(key, default)

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route("/api/register", methods=["POST"])
def register():
    fullname = get_request_value("fullname")
    email = get_request_value("email")
    phone = get_request_value("phone")
    password = get_request_value("password")

    if not (fullname and email and phone and password):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    try:
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO users(fullname, email, phone, password) VALUES (%s,%s,%s,%s)",
            (fullname, email, phone, password)
        )
        db.commit()
        cur.close()
    except mysql.connector.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "success", "message": "Registration successful"})

@app.route("/api/login", methods=["POST"])
def login():
    email = get_request_value("email")
    password = get_request_value("password")

    if not (email and password):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT email, password FROM users WHERE email=%s", (email,))
        row = cur.fetchone()
        cur.close()
    except mysql.connector.Error as e:
        return jsonify({"status": "error", "message": str(e)})

    if not row:
        return jsonify({"status": "error", "message": "User not found"}), 404

    if password == row["password"]:
        session["email"] = email
        return jsonify({"status": "success", "message": "Login successful"})

    return jsonify({"status": "error", "message": "Wrong password"}), 401

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files or request.files['image'].filename == "":
        return render_template("result.html",
                               image_path=None,
                               disease_name="⚠️ No image uploaded",
                               description="No description available",
                               fertilizer_recommendation="N/A")

    image_file = request.files['image']
    filename = secure_filename(image_file.filename)

    if not allowed_file(filename):
        return render_template("result.html",
                               image_path=None,
                               disease_name="⚠️ Unsupported File",
                               description="Invalid image format.",
                               fertilizer_recommendation="N/A")

    save_path = os.path.join(UPLOAD_FOLDER, filename)
    image_file.save(save_path)

    filename_lower = filename.lower()
    row = df_dataset[df_dataset["image_name"] == filename_lower]

    if not row.empty:
        row_info = row.iloc[0]
        disease_name = row_info.get("disease_name")
        description = row_info.get("description")
        fertilizer = row_info.get("fertilizer_recommendation")
    else:
        disease_name = "Unknown Disease"
        description = "No description available"
        fertilizer = "General NPK recommended"

    email = session.get("email", "unknown_user")

    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            INSERT INTO image_logs(email, image_name, disease_name, description, fertilizer)
            VALUES (%s, %s, %s, %s, %s)
        """, (email, filename, disease_name, description, fertilizer))
        db.commit()
        cur.close()
    except:
        pass

    return render_template("result.html",
                           image_path=f"/uploads/{filename}",
                           disease_name=disease_name,
                           description=description,
                           fertilizer_recommendation=fertilizer)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True)


