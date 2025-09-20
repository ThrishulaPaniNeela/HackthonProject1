from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_issue():
    title = request.form['title']
    description = request.form['description']
    location = request.form['location']
    # For now, just print instead of saving
    print("Issue submitted:", title, description, location)
    return "Issue Submitted Successfully!"

if __name__ == '__main__':
    app.run(debug=True)
