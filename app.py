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


# nuevo producto 
@app.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        data = ()
        # codigo = request.form["codigo"]
        # nombre = request.form["nombre"]
        # precio = request.form["precio"]
        # categoria = request.form["categoria"]
        # existencia = request.form["existencia"]
        # activo = request.form["activo"]
        
        # form
        data = (
            str(request.form["codigo"]),
            str(request.form["nombre"]),
            float(request.form["precio"]) or 0,
            str(request.form["categoria"]),
            int(request.form["existencia"]) or 0,
            bool(request.form["activo"])

        )
        print(data)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""INSERT INTO productos (codigo, nombre, precio, categoria, existencia, activo) 
                    VALUES (%s, %s, %s, %s,%s,%s)""", data)
        conn.commit()
        cur.close()
        conn.close()
        flash("Producto registrado exitosamente")
        return redirect(url_for("index"))
    return render_template("form.html")

        
# @app.route("/editar", methods=["GET", "POST"])
# def editar():
#     if request.method == "POST":
#         # form
#         data = (
#             str(request.form["codigo"]),
#             str(request.form["nombre"]),
#             float(request.form["precio"]) or 0,
#             str(request.form["categoria"]),
#             int(request.form["existencia"]) or 0,
#             bool(request.form["activo"])


if __name__ == "__main__":
    app.run(debug=True)