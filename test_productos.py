import unittest
from unittest.mock import MagicMock, patch
from app import app


class ProductosTest(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, SECRET_KEY="test")
        self.client = app.test_client()
        self.conn = MagicMock()
        self.cur = self.conn.cursor.return_value
        self.producto = dict(id=7, codigo="A1", nombre="Monitor", precio=100,
                             categoria="Pantallas", existencia=3, activo=True)
        self.cur.fetchone.return_value = self.producto
        self.cur.fetchall.return_value = [self.producto]
        patcher = patch("app.get_connection", return_value=self.conn)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_editar_carga_producto(self):
        response = self.client.get("/producto/editar/7")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'value="Monitor"', response.data)
        self.cur.execute.assert_called_once_with(
            "SELECT * FROM productos WHERE id=%s", (7,))

    def test_editar_guarda_y_desactiva(self):
        response = self.client.post("/producto/editar/7", data=dict(
            codigo="B2", nombre="Teclado", precio="25.50",
            categoria="Accesorios", existencia="4"))
        self.assertEqual(response.status_code, 302)
        sql, params = self.cur.execute.call_args.args
        self.assertIn("WHERE id=%s", sql)
        self.assertEqual(params, ("B2", "Teclado", 25.5, "Accesorios", 4, False, 7))
        self.conn.commit.assert_called_once()

    def test_editar_inexistente(self):
        self.cur.fetchone.return_value = None
        for method in (self.client.get, self.client.post):
            self.assertEqual(method("/producto/editar/999").status_code, 404)
        self.conn.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
