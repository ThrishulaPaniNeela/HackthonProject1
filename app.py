from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"  # change in production


# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect("civic_issues.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    location TEXT NOT NULL,
                    status TEXT DEFAULT "Pending"
                )''')
    conn.commit()
    conn.close()


# ---------- Home (Citizen Side) ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]

        conn = sqlite3.connect("civic_issues.db")
        c = conn.cursor()
        c.execute("INSERT INTO issues (title, description, location) VALUES (?, ?, ?)",
                  (title, description, location))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    conn = sqlite3.connect("civic_issues.db")
    c = conn.cursor()
    c.execute("SELECT * FROM issues")
    issues = [{"id": row[0], "title": row[1], "description": row[2], "location": row[3], "status": row[4]}
              for row in c.fetchall()]
    conn.close()

    return render_template("index.html", issues=issues, user=session.get("user"))


# ---------- Admin Login ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Hardcoded admin (change as needed)
        if username == "admin" and password == "admin123":
            session["user"] = "admin"
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# ---------- Admin Dashboard ----------
@app.route("/admin")
def admin_dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("civic_issues.db")
    c = conn.cursor()
    c.execute("SELECT * FROM issues")
    issues = [{"id": row[0], "title": row[1], "description": row[2], "location": row[3], "status": row[4]}
              for row in c.fetchall()]
    conn.close()

    return render_template("admin.html", issues=issues)


# ---------- Update Issue Status ----------
@app.route("/resolve/<int:issue_id>")
def resolve(issue_id):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("civic_issues.db")
    c = conn.cursor()
    c.execute("UPDATE issues SET status='Resolved' WHERE id=?", (issue_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard"))


# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
