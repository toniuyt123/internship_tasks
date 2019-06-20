import psycopg2
from flask import Flask, render_template
from config import config

app = Flask(__name__)

@app.route('/')
def index():
    return 0

@app.route('/register')
def register():
    return render_template('register.html')

if __name__ == '__main__':
    app.run()