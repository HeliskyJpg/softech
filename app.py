import os
import re
from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from db import get_connection
import psycopg2.extras
from psycopg2.errors import UniqueViolation
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.secret_key = user=os.getenv("SECRET_KEY")

def validar_producto(form):
    codigo = form.get("codigo", "").strip()
    if not codigo or len(codigo) > 120:
        return "El codigo es obligatorio y debe tener como maximo 120 caracteres."
    if len(form.get("nombre", "")) > 120:
        return "El nombre debe tener como maximo 120 caracteres."
    if len(form.get("categoria", "")) > 50:
        return "La categoria debe tener como maximo 50 caracteres."
    precio = form.get("precio", "").strip() or "0"
    if not re.fullmatch(r"[0-9]{1,10}(\.[0-9]{1,2})?", precio):
        return "El precio debe estar entre 0 y 9999999999.99, con hasta dos decimales."
    existencia = form.get("existencia", "").strip()
    if not re.fullmatch(r"[0-9]{1,10}", existencia):
        return "La existencia debe ser un numero entero entre 1 y 2147483647."
    if not 1 <= int(existencia) <= 2147483647:
        return "La existencia debe estar entre 1 y 2147483647."
    return None

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
        error = validar_producto(request.form)
        if error:
            flash(error, "danger")
            return redirect(url_for("nuevo"))
        existencia = int(request.form["existencia"])
        data = ()
        # codigo = request.form["codigo"]
        # nombre = request.form["nombre"]
        # precio = request.form["precio"]
        # categoria = request.form["categoria"]
        # existencia = request.form["existencia"]
        # activo = request.form["activo"]
        
        # form
        data = (
            request.form["codigo"].strip(),
            request.form.get("nombre", ""),
            Decimal(request.form.get("precio", "").strip() or "0"),
            request.form.get("categoria", ""),
            existencia,
            bool(request.form["activo"])

        )
        print(data)
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""INSERT INTO productos (codigo, nombre, precio, categoria, existencia, activo)
                        VALUES (%s, %s, %s, %s,%s,%s)""", data)
            conn.commit()
        except UniqueViolation as error:
            conn.rollback()
            if error.diag.constraint_name != "productos_codigo_key":
                raise
            flash("Ya existe un producto con ese codigo.", "danger")
            return redirect(url_for("nuevo"))
        finally:
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
        error = validar_producto(request.form)
        if error:
            cur.close(); conn.close()
            flash(error, "danger")
            return redirect(url_for("editar", id=id))
        existencia = int(request.form["existencia"])
        # form
        data = (
            request.form["codigo"].strip(),
            request.form.get("nombre", ""),
            Decimal(request.form.get("precio", "").strip() or "0"),
            request.form.get("categoria", ""),
            existencia,
            "activo" in request.form,
            id
        )
        try:
            cur.execute("""UPDATE productos SET codigo=%s, nombre=%s, precio=%s, categoria=%s, existencia=%s, activo=%s
            WHERE id=%s""",data)
            conn.commit()
        except UniqueViolation as error:
            conn.rollback()
            if error.diag.constraint_name != "productos_codigo_key":
                raise
            flash("Ya existe un producto con ese codigo.", "danger")
            return redirect(url_for("editar", id=id))
        finally:
            cur.close()
            conn.close()
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
