from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ----------------- File Upload Setup -----------------
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------- Database Setup -----------------
DB_NAME = "civic_issues.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            photo TEXT,
            status TEXT DEFAULT "Pending"
        )
    ''')
    conn.commit()
    conn.close()

# ----------------- Routes -----------------
# Citizen View (Home)
@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        location = request.form.get("location")

        # Handle photo upload
        photo_file = request.files.get("photo")
        photo_filename = None
        if photo_file and allowed_file(photo_file.filename):
            photo_filename = secure_filename(photo_file.filename)
            photo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))

        # Save issue to DB
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO issues (title, description, location, photo) VALUES (?, ?, ?, ?)",
                  (title, description, location, photo_filename))
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    # Fetch all issues
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM issues")
    rows = c.fetchall()
    issues = [{"id": r[0], "title": r[1], "description": r[2], "location": r[3], "photo": r[4], "status": r[5]} for r in rows]
    conn.close()

    return render_template("index.html", issues=issues, user=session.get("user"))

# Admin Login
@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "admin123":
            session["user"] = "admin"
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Invalid credentials"
    return render_template("login.html", error=error)

# Admin Dashboard
@app.route("/admin")
def admin_dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM issues")
    rows = c.fetchall()
    issues = [{"id": r[0], "title": r[1], "description": r[2], "location": r[3], "photo": r[4], "status": r[5]} for r in rows]
    conn.close()

    return render_template("admin.html", issues=issues)

# Mark Issue as Resolved
@app.route("/resolve/<int:issue_id>")
def resolve(issue_id):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE issues SET status='Resolved' WHERE id=?", (issue_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard"))

# Admin Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

# ----------------- Run App -----------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
