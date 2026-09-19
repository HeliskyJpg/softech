# Tecsoft

Proyecto  para registrar, editar, eliminar y buscar productos.
Esta hecho con Flask, PostgreSQL y Bootstrap.

Para iniciarlo, instala las dependencias con `pip install -r requirements.txt`,
configura la conexion a la base de datos en `.env` y ejecuta `python app.py`.
Luego abre http://127.0.0.1:5000 en el navegador.

En `app.py` se usa `app.run(debug=True)`. Esto permite ver los errores y
recargar la aplicacion al guardar cambios. Lo dejamos activo mientras
desarrollamos; no se debe usar en produccion.
