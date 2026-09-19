import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from db import get_connection
import psycopg2.extras
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.secret_key = user=os.getenv("SECRET_KEY")

@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if q:
        patron = "%" + q.replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%"
        cur.execute("""SELECT * FROM productos
                    WHERE codigo ILIKE %s ESCAPE '!'
                       OR nombre ILIKE %s ESCAPE '!'
                       OR categoria ILIKE %s ESCAPE '!'
                    ORDER BY id DESC""", (patron, patron, patron))
    else:
        cur.execute("SELECT * FROM productos ORDER BY id DESC")
    productos = cur.fetchall()
    cur.close(); conn.close()
    return render_template("home.html", productos=productos, q=q)


# nuevo producto 
@app.route("/producto", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        existencia = int(request.form.get("existencia") or 0)
        if existencia < 0:
            flash("La existencia no puede ser negativa.", "danger")
            return redirect(url_for("nuevo"))
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
            existencia,
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

        
@app.route("/producto/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM productos WHERE id=%s", (id,))
    producto = cur.fetchone()
    if producto is None:
        cur.close(); conn.close()
        abort(404)
    if request.method == "POST":
        existencia = int(request.form.get("existencia") or 0)
        if existencia < 0:
            cur.close(); conn.close()
            flash("La existencia no puede ser negativa.", "danger")
            return redirect(url_for("editar", id=id))
        # form
        data = (
            str(request.form["codigo"]),
            str(request.form["nombre"]),
            float(request.form.get("precio") or 0),
            str(request.form["categoria"]),
            existencia,
            "activo" in request.form,
            id
        )
        cur.execute("""UPDATE productos SET codigo=%s, nombre=%s, precio=%s, categoria=%s, existencia=%s, activo=%s
        WHERE id=%s""",data)
        conn.commit(); cur.close(); conn.close()
        flash("Producto editado exitosamente")
        return redirect(url_for("index"))
    cur.close(); conn.close()
    return render_template("form.html", producto=producto)



@app.route("/producto/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM productos WHERE id=%s RETURNING id", (id,))
            if cur.fetchone() is None:
                abort(404)
        conn.commit()
    finally:
        conn.close()
    flash("Producto eliminado exitosamente")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
