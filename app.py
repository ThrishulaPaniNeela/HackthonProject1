from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///issues.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model (table structure)
class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(200))
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default="Pending")  # New column for status

# Home page → form + list issues
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

    issues = Issue.query.all()  # fetch all issues from DB
    return render_template("index.html", issues=issues)

# Route to resolve issue
@app.route("/resolve/<int:issue_id>")
def resolve_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    issue.status = "Resolved"
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # creates table if not exists
    app.run(debug=True)
