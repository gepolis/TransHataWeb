from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'GU_GEPOLIS_GUAPPSUPPORT_ADMIN_SECRET_KEY_2'

@app.route('/')
def hello_world():  # put application's code here
    return render_template("index.html")

@app.route('/new')
def new():  # put application's code here
    return render_template("new.html")

@app.route('/purple')
def purple():  # put application's code here
    return render_template("purple.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)