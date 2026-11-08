# API REST de Personas y Pizzas

Trabajo práctico de Taller de Programación II (Universidad FASTA).

API REST en Python que administra personas y las pizzas que pidió cada una (relación 1 a N).
Usa Flask, Connexion 2 (contrato OpenAPI en `swagger.yml`), SQLAlchemy, Marshmallow y SQLite.

## Requisitos

- Python 3.10 o superior (probado con Python 3.14)
- pip

## Instalación

Desde una terminal abierta en la carpeta del proyecto:

```bash
# 1. Crear el entorno virtual (una sola vez)
python -m venv venv

# 2. Activarlo (cada vez que abras una terminal nueva)
venv\Scripts\Activate.ps1        # Windows (PowerShell)
source venv/bin/activate         # macOS / Linux

# 3. Instalar las dependencias
pip install -r requirements.txt
```

> En Windows, si PowerShell no deja ejecutar `Activate.ps1`, correr una vez
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## Crear la base de datos

```bash
python build_database.py
```

Crea `people.db` con 3 personas y 7 pizzas de ejemplo. **Borra todo lo que hubiera antes**:
usarlo para empezar de cero, o después de cambiar `models.py`.

## Levantar la API

```bash
python app.py
```

| URL | Qué es |
|-----|--------|
| http://localhost:8000/ | Página de inicio con las personas y sus pizzas |
| http://localhost:8000/api/ui/ | Swagger UI: documentación interactiva para probar la API |
| http://localhost:8000/api/openapi.json | Contrato OpenAPI en JSON |

El servidor se detiene con `Ctrl + C`.

## Pruebas automáticas (pytest)

[pytest](https://docs.pytest.org/) es la herramienta que ejecuta las pruebas automáticas.
Las pruebas están en `tests/test_api.py` y usan el cliente de pruebas de Flask
(`app.test_client()`), que hace peticiones HTTP a la API sin necesidad de levantar el servidor.

Para correrlas, con el entorno virtual activado y desde la carpeta del proyecto:

```bash
pytest
```

Si todo está bien termina con `25 passed`. Para ver el nombre de cada prueba: `pytest -v`.

Cada prueba arranca con una base de datos nueva **en memoria** y con los datos de ejemplo,
así que las pruebas no dependen unas de otras y **no modifican `people.db`**.
La base se elige con la variable de entorno `DATABASE_URL` (ver `config.py`).

Cubren: listar y crear personas, apellido duplicado (406), persona inexistente (404),
crear pizza, pizza con persona inexistente (404), precio y tamaño inválidos (400),
textos vacíos (400), actualizar y borrar, borrado en cascada y los tres endpoints nuevos.

## Endpoints

Todas las rutas empiezan con `/api`.

| Método | Ruta | Qué hace | Respuestas |
|--------|------|----------|------------|
| GET | `/people` | Lista todas las personas con sus pizzas | 200 |
| POST | `/people` | Crea una persona (`lname` obligatorio, `fname`) | 201, 400, 406 |
| GET | `/people/{lname}` | Consulta una persona por apellido | 200, 404 |
| PUT | `/people/{lname}` | Cambia el nombre (`fname`) de una persona | 200, 400, 404 |
| DELETE | `/people/{lname}` | Borra una persona y todas sus pizzas | 204, 404 |
| GET | `/people/{lname}/pizzas` | Lista las pizzas de una persona | 200, 404 |
| GET | `/people/{lname}/resumen` | Cantidad de pizzas y total gastado | 200, 404 |
| GET | `/pizzas` | Lista todas las pizzas; acepta `?person_id=N` para filtrar | 200, 400, 404 |
| POST | `/pizzas` | Crea una pizza (`person_id`, `content`, `price` obligatorios; `size`) | 201, 400, 404 |
| GET | `/pizzas/{pizza_id}` | Consulta una pizza por ID | 200, 404 |
| PUT | `/pizzas/{pizza_id}` | Modifica una pizza (`content`, `price` obligatorios; `size`) | 200, 400, 404 |
| DELETE | `/pizzas/{pizza_id}` | Borra una pizza | 204, 404 |

Reglas de los datos:

- `lname` y `content` no pueden estar vacíos.
- `price` es un número mayor que 0.
- `size` solo puede ser `chica`, `mediana` o `grande`.

Ejemplo:

```bash
curl -X POST http://localhost:8000/api/pizzas \
  -H "Content-Type: application/json" \
  -d '{"person_id": 2, "content": "Pizza Fugazzeta", "price": 9800, "size": "mediana"}'
```

## Estructura

```
├── app.py               Punto de entrada: registra el contrato y la página de inicio
├── config.py            Crea la app Flask/Connexion, la base y Marshmallow
├── models.py            Tablas Person y Pizza, y sus esquemas de Marshmallow
├── people.py            Lógica de los endpoints de personas
├── pizzas.py            Lógica de los endpoints de pizzas
├── build_database.py    Crea la base con datos de ejemplo
├── swagger.yml          Contrato OpenAPI 3 de la API
├── requirements.txt     Dependencias
├── pytest.ini           Configuración de pytest
├── templates/home.html  Página de inicio
├── tests/test_api.py    Pruebas automáticas
└── informe/             Informe y capturas
```
