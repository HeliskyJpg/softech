import os
from flask import Flask, render_template, request, redirect, url_for, flash
from db import get_connection
import psycopg2.extras
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.secret_key = user=os.getenv("SECRET_KEY")

@app.route("/")
def index():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM productos ORDER BY id DESC")
    productos = cur.fetchall()
    cur.close(); conn.close()
    return render_template("home.html", productos=productos)

if __name__ == "__main__":
    app.run(debug=True)