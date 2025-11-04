import pytest
from app import app as flask_app


@pytest.fixture
def client():
    """
    Crea y configura un cliente de pruebas para la aplicación Flask.
    Este cliente permite realizar solicitudes HTTP simuladas sin ejecutar el servidor real.

    Returns:
        FlaskClient: Objeto de prueba que puede realizar peticiones (GET, POST, PUT, DELETE)
        contra las rutas de la aplicación Flask.
    """
    flask_app.testing = True
    return flask_app.test_client()


import json
import app as app_module

def test_homepage_renders():
    """
    Prueba que la página de inicio ("/") se renderiza correctamente y contiene el texto esperado.
    "
    """
    app = app_module.app
    client = app.test_client()
    r = client.get("/")
    assert r.status_code == 200
    assert b"Mini To-Do" in r.data  

def test_create_task_api():
    """
    Prueba la creación de una nueva tarea a través de la API RESTful.
    Verifica que la tarea se crea correctamente y que se puede recuperar posteriormente.
    """
    
    app_module.TAREAS.clear()  
    app = app_module.app
    client = app.test_client()

    r = client.post("/api/tareas", json={"texto": "Probar test"})
    assert r.status_code == 201
    data = r.get_json()
    assert data["ok"] is True
    assert data["data"]["texto"] == "Probar test"

    r = client.get("/api/tareas")
    listado = r.get_json()["data"]
    assert len(listado) == 1
    assert listado[0]["texto"] == "Probar test"