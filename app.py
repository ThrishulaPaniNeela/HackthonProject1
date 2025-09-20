from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for login sessions

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///issues.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Models
class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(200))
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default="Pending")

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

@login_manager.user_loader
def load_user(admin_id):
    return Admin.query.get(int(admin_id))

# Home page (citizen view)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]

        new_issue = Issue(title=title, description=description, location=location)
        db.session.add(new_issue)
        db.session.commit()

        return redirect(url_for("index"))

    issues = Issue.query.all()
    return render_template("index.html", issues=issues, user=current_user)

# Admin login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            login_user(admin)
            return redirect(url_for("index"))
        else:
            return "Invalid credentials!"

    return render_template("login.html")

# Admin logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# Mark issue as resolved (only admin)
@app.route("/resolve/<int:issue_id>")
@login_required
def resolve_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    issue.status = "Resolved"
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Add a default admin (only once)
        if not Admin.query.filter_by(username="admin").first():
            db.session.add(Admin(username="admin", password="admin123"))
            db.session.commit()
    app.run(debug=True)
