# Parte 1 – Diagnóstico (borrador para el informe)

Pruebas hechas sobre la base recién creada con `python build_database.py`,
desde Swagger UI (http://localhost:8000/api/ui/). Las capturas están en `informe/capturas/`.

## Tabla: código declarado en swagger.yml vs. código real

| # | Endpoint | Prueba | Declara swagger.yml | Devuelve la API | ¿Coincide? | Captura |
|---|----------|--------|---------------------|-----------------|------------|---------|
| 1 | GET /api/people | Listar personas | 200 | 200 | Sí | 01_get_people.png |
| 2 | GET /api/people/{lname} | `Gomez` | 200 | 200 | Sí | 02a_get_person.png |
|   |  | `AlgoQueNoExiste` | (no declara errores) | 404 | No documentado | 02b_get_person_404.png |
| 3 | POST /api/people | `{"lname":"Corrente","fname":"Pablo"}` | 201 | 201 | Sí | 03a_post_person_a.png, 03a_post_person_b.png |
|   |  | mismo apellido otra vez | (no declara errores) | 406 | No documentado | 03b_post_person_406.png |
|   |  | `{"fname":"Pablo"}` (sin lname) | (no declara errores) | 400 | No documentado | 03c_post_person_400_a.png, 03c_post_person_400_b.png |
| 4 | PUT /api/people/{lname} | `Corrente` → `{"lname":"Corrente","fname":"Pablo Martin"}` | **200** | **201** | **No** | 04_put_person_a.png, 04_put_person_b.png |
| 5 | DELETE /api/people/{lname} | `Corrente` | **204** | **200** + texto | **No** | 05_delete_person.png |
| 6 | POST /api/pizzas | `{"person_id":2,"content":"Pizza Fugazzeta"}` | 201 | 201 | Sí | 06a_post_pizza.png |
|   |  | `{"person_id":99,"content":"Pizza X"}` | (no declara errores) | 404 | No documentado | 06b_post_pizza_404.png |
|   |  | `{"person_id":2}` (sin content) | 201 | **500** | **No** | 06c_post_pizza_500_a.png, 06c_post_pizza_500_b.png |
| 7 | GET /api/pizzas/{pizza_id} | `1` | 200 | 200 | Sí | 07a_get_pizza.png |
|   |  | `999` | (no declara errores) | 404 | No documentado | 07b_get_pizza_404.png |
| 8 | PUT /api/pizzas/{pizza_id} | `1` → `{"content":"Pizza Napolitana"}` | **200** | **201** | **No** | 08_put_pizza.png |
| 9 | DELETE /api/pizzas/{pizza_id} | `8` (la Fugazzeta creada en 6) | 204 | 204 | Sí | 09_delete_pizza.png |

## Diferencias encontradas (con evidencia)

**D1. PUT /api/people/{lname} devuelve 201 en vez de 200.**
Petición: `PUT /api/people/Corrente` con `{"lname":"Corrente","fname":"Pablo Martin"}`.
Respuesta real: `201 CREATED` con la persona actualizada. El contrato declara `200`.
201 significa "creado"; una actualización no crea nada, así que lo correcto es 200.

**D2. PUT /api/pizzas/{pizza_id} devuelve 201 en vez de 200.**
Petición: `PUT /api/pizzas/1` con `{"content":"Pizza Napolitana"}`.
Respuesta real: `201 CREATED`. El contrato declara `200`.

**D3. DELETE /api/people/{lname} devuelve 200 con un texto en vez de 204.**
Petición: `DELETE /api/people/Corrente`.
Respuesta real: `200 OK` con el texto `Corrente successfully deleted` (`text/html`, no JSON).
El contrato declara `204` (sin contenido). Además es inconsistente con DELETE de pizzas, que sí devuelve 204.

**D4. Ningún endpoint documenta sus respuestas de error.**
La API devuelve 404 (persona/pizza inexistente), 406 (apellido duplicado) y 400
(falta un campo obligatorio o tipo inválido), pero en swagger.yml solo figura el código de éxito.
Ejemplo: `GET /api/people/AlgoQueNoExiste` → `404` con
`{"detail": "Person with last name AlgoQueNoExiste not found", ...}`.

**D5. POST /api/pizzas sin `content` rompe el servidor (500).**
Petición: `POST /api/pizzas` con `{"person_id": 2}`.
Respuesta real: `500 INTERNAL SERVER ERROR` con la página del depurador de Werkzeug
(`marshmallow.exceptions.ValidationError: {'content': ['Missing data for required field.']}`).
El contrato no marca `content` como obligatorio, pero el modelo sí (`nullable=False`).
Debería rechazarse con 400 desde el contrato. Lo mismo pasa con `PUT /api/pizzas/1` y cuerpo `{}`.

**D6. POST /api/pizzas sin `person_id` devuelve 404 en vez de 400.**
Petición: `POST /api/pizzas` con `{"content": "Pizza X"}`.
Respuesta real: `404` con `Person not found for ID: None`. Falta un dato obligatorio,
así que debería ser 400; el contrato no marca `person_id` como requerido.

**D7. PUT /api/people/{lname} exige `lname` en el cuerpo pero lo ignora.**
Petición: `PUT /api/people/Corrente` con `{"lname":"OtroApellido","fname":"Pablo"}`.
Respuesta real: `201` y la persona sigue llamándose `Corrente`. El contrato obliga a mandar
un dato que no se usa, sin avisar.

**D8. El esquema de respuesta no está documentado.**
El esquema `Person` solo describe `fname` y `lname`, pero la API devuelve también `id`,
`timestamp` y `pizzas`. No existe un esquema `Pizza`: los endpoints de pizzas definen
el cuerpo "a mano" cada vez.

**D9. Se aceptan valores vacíos.**
`POST /api/people` con `{"lname":"","fname":"Vacio"}` → `201` (se crea una persona sin apellido).
`POST /api/pizzas` con `{"person_id":2,"content":""}` → `201` (pizza sin descripción).

**D10. No existe GET /api/pizzas.**
`GET /api/pizzas` → `405 Method Not Allowed`. No hay forma de listar todas las pizzas.

**D11. Los mensajes de error están en inglés**, mientras que la documentación y los datos están en español.

**D12. El error 500 expone información interna del servidor.**
En la respuesta de `POST /api/pizzas` con `{"person_id": 2}` (captura 06c) aparece la página del
depurador de Werkzeug, que muestra rutas internas de la computadora
(`C:\Users\...\venv\Lib\site-packages\flask\app.py`) y el código fuente. Pasa porque `app.py`
arranca con `debug=True`. Un cliente nunca debería ver esto.

**D13. DELETE /api/pizzas/{pizza_id} responde 204 pero con `content-type: text/html`.**
El código arma un mensaje de texto (`"8 successfully deleted"`) que nunca llega al cliente,
porque una respuesta 204 no puede tener cuerpo (captura 09). Es código que no sirve.
