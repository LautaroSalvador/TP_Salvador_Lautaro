"""Pruebas automáticas de la API de Personas y Pizzas.

Se ejecutan con el comando `pytest` desde la carpeta del proyecto.
Usan una base de datos en memoria, así que NO tocan people.db.
"""

import os

# Antes de importar la app: usar una base en memoria solo para las pruebas
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest  # noqa: E402

import app as app_module  # noqa: E402,F401  (registra las rutas de swagger.yml)
from build_database import crear_base  # noqa: E402
from config import app as flask_app  # noqa: E402


@pytest.fixture
def client():
    """Antes de cada prueba: base nueva con los datos de ejemplo y un cliente HTTP de prueba."""
    with flask_app.app_context():
        crear_base()
    return flask_app.test_client()


# ---------------------------------------------------------------- Personas


def test_listar_personas(client):
    respuesta = client.get("/api/people")

    assert respuesta.status_code == 200
    apellidos = [persona["lname"] for persona in respuesta.get_json()]
    assert apellidos == ["Sanchez", "Gomez", "Lopez"]


def test_crear_persona(client):
    respuesta = client.post("/api/people", json={"lname": "Corrente", "fname": "Pablo"})

    assert respuesta.status_code == 201
    persona = respuesta.get_json()
    assert persona["lname"] == "Corrente"
    assert persona["pizzas"] == []
    # y ahora se puede consultar
    assert client.get("/api/people/Corrente").status_code == 200


def test_crear_persona_con_apellido_duplicado_devuelve_406(client):
    respuesta = client.post("/api/people", json={"lname": "Gomez", "fname": "Otra"})

    assert respuesta.status_code == 406
    assert respuesta.get_json()["detail"] == "Ya existe una persona con apellido Gomez"


def test_crear_persona_con_apellido_vacio_devuelve_400(client):
    assert client.post("/api/people", json={"lname": "", "fname": "Ana"}).status_code == 400
    assert client.post("/api/people", json={"lname": "   ", "fname": "Ana"}).status_code == 400


def test_consultar_persona_inexistente_devuelve_404(client):
    respuesta = client.get("/api/people/NoExiste")

    assert respuesta.status_code == 404
    assert respuesta.get_json()["detail"] == "No existe una persona con apellido NoExiste"


def test_actualizar_persona_devuelve_200(client):
    respuesta = client.put("/api/people/Gomez", json={"fname": "Cintia"})

    assert respuesta.status_code == 200
    assert respuesta.get_json()["fname"] == "Cintia"


def test_borrar_persona_borra_sus_pizzas_en_cascada(client):
    pizzas_de_gomez = [p["id"] for p in client.get("/api/people/Gomez/pizzas").get_json()]
    assert len(pizzas_de_gomez) == 2

    respuesta = client.delete("/api/people/Gomez")

    assert respuesta.status_code == 204
    assert client.get("/api/people/Gomez").status_code == 404
    for pizza_id in pizzas_de_gomez:
        assert client.get(f"/api/pizzas/{pizza_id}").status_code == 404


# ---------------------------------------------------------------- Pizzas


def test_crear_pizza(client):
    nueva = {"person_id": 2, "content": "Pizza Fugazzeta", "price": 9800, "size": "mediana"}

    respuesta = client.post("/api/pizzas", json=nueva)

    assert respuesta.status_code == 201
    pizza = respuesta.get_json()
    assert pizza["content"] == "Pizza Fugazzeta"
    assert pizza["price"] == 9800
    assert pizza["size"] == "mediana"
    assert pizza["person_id"] == 2


def test_crear_pizza_para_persona_inexistente_devuelve_404(client):
    nueva = {"person_id": 99, "content": "Pizza X", "price": 9000}

    respuesta = client.post("/api/pizzas", json=nueva)

    assert respuesta.status_code == 404
    assert respuesta.get_json()["detail"] == "No existe una persona con ID 99"


@pytest.mark.parametrize("precio", [-500, 0, "caro"])
def test_crear_pizza_con_precio_invalido_devuelve_400(client, precio):
    nueva = {"person_id": 2, "content": "Pizza X", "price": precio, "size": "grande"}

    assert client.post("/api/pizzas", json=nueva).status_code == 400


def test_crear_pizza_sin_precio_devuelve_400(client):
    nueva = {"person_id": 2, "content": "Pizza X", "size": "grande"}

    assert client.post("/api/pizzas", json=nueva).status_code == 400


def test_crear_pizza_con_tamano_invalido_devuelve_400(client):
    nueva = {"person_id": 2, "content": "Pizza X", "price": 9000, "size": "gigante"}

    assert client.post("/api/pizzas", json=nueva).status_code == 400


def test_crear_pizza_con_contenido_vacio_devuelve_400(client):
    for contenido in ["", "   "]:
        nueva = {"person_id": 2, "content": contenido, "price": 9000}
        assert client.post("/api/pizzas", json=nueva).status_code == 400


def test_actualizar_pizza_devuelve_200(client):
    cambios = {"content": "Pizza Napolitana", "price": 10200, "size": "grande"}

    respuesta = client.put("/api/pizzas/1", json=cambios)

    assert respuesta.status_code == 200
    assert respuesta.get_json()["content"] == "Pizza Napolitana"
    assert respuesta.get_json()["price"] == 10200


def test_borrar_pizza_devuelve_204(client):
    assert client.delete("/api/pizzas/1").status_code == 204
    assert client.get("/api/pizzas/1").status_code == 404


def test_consultar_pizza_inexistente_devuelve_404(client):
    respuesta = client.get("/api/pizzas/999")

    assert respuesta.status_code == 404
    assert respuesta.get_json()["detail"] == "No existe una pizza con ID 999"


# ---------------------------------------------------------------- Endpoints nuevos (Parte 3)


def test_listar_todas_las_pizzas(client):
    respuesta = client.get("/api/pizzas")

    assert respuesta.status_code == 200
    assert len(respuesta.get_json()) == 7


def test_listar_pizzas_filtrando_por_persona(client):
    respuesta = client.get("/api/pizzas?person_id=2")

    assert respuesta.status_code == 200
    pizzas = respuesta.get_json()
    assert len(pizzas) == 2
    assert all(pizza["person_id"] == 2 for pizza in pizzas)


def test_listar_pizzas_de_persona_inexistente_por_id_devuelve_404(client):
    assert client.get("/api/pizzas?person_id=99").status_code == 404


def test_listar_pizzas_de_una_persona(client):
    respuesta = client.get("/api/people/Lopez/pizzas")

    assert respuesta.status_code == 200
    contenidos = {pizza["content"] for pizza in respuesta.get_json()}
    assert contenidos == {"Pizza Arrollada", "Pizza Cuatro Quesos"}


def test_listar_pizzas_de_persona_inexistente_devuelve_404(client):
    assert client.get("/api/people/NoExiste/pizzas").status_code == 404


def test_resumen_de_persona(client):
    respuesta = client.get("/api/people/Sanchez/resumen")

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {
        "lname": "Sanchez",
        "fname": "Ricardo",
        "cantidad_pizzas": 3,
        "total_gastado": 28500,  # 9500 + 8200 + 10800
    }


def test_resumen_de_persona_inexistente_devuelve_404(client):
    assert client.get("/api/people/NoExiste/resumen").status_code == 404


# ---------------------------------------------------------------- Paginación (Parte 6)


def test_paginar_personas_con_limit(client):
    respuesta = client.get("/api/people?limit=2")

    assert respuesta.status_code == 200
    assert [p["lname"] for p in respuesta.get_json()] == ["Sanchez", "Gomez"]


def test_paginar_personas_con_limit_y_offset(client):
    respuesta = client.get("/api/people?limit=2&offset=2")

    assert respuesta.status_code == 200
    assert [p["lname"] for p in respuesta.get_json()] == ["Lopez"]


def test_paginar_pizzas_con_limit_y_offset(client):
    respuesta = client.get("/api/pizzas?limit=3&offset=3")

    assert respuesta.status_code == 200
    assert [pizza["id"] for pizza in respuesta.get_json()] == [4, 5, 6]


def test_paginar_pizzas_de_una_persona(client):
    respuesta = client.get("/api/pizzas?person_id=1&limit=2&offset=1")

    assert respuesta.status_code == 200
    assert [pizza["id"] for pizza in respuesta.get_json()] == [2, 3]


def test_offset_mayor_que_la_cantidad_devuelve_lista_vacia(client):
    respuesta = client.get("/api/pizzas?offset=100")

    assert respuesta.status_code == 200
    assert respuesta.get_json() == []


@pytest.mark.parametrize("parametros", ["limit=0", "limit=-1", "offset=-1", "limit=abc"])
def test_paginacion_con_valores_invalidos_devuelve_400(client, parametros):
    assert client.get(f"/api/people?{parametros}").status_code == 400
    assert client.get(f"/api/pizzas?{parametros}").status_code == 400
