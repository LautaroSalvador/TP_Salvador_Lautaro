# Parte 2 – Alinear contrato y código (borrador para el informe)

Criterio general: el contrato (`swagger.yml`) es la fuente de verdad (enfoque *contract first*).
Se cambia el **código** cuando el contrato describe el comportamiento correcto según HTTP,
y se cambia el **contrato** cuando el código hace lo correcto pero el contrato no lo documenta
o lo documenta mal.

## Decisiones por diferencia

| # | Diferencia | Qué se cambió | Justificación |
|---|-----------|---------------|---------------|
| D1 | PUT /people/{lname} devolvía 201, el contrato dice 200 | **Código** (`people.update` devuelve 200) | 201 *Created* indica que se creó un recurso nuevo. Un PUT sobre una persona existente solo la modifica, así que la respuesta correcta es 200 *OK*. El contrato tenía razón. |
| D2 | PUT /pizzas/{pizza_id} devolvía 201, el contrato dice 200 | **Código** (`pizzas.update` devuelve 200) | Mismo motivo que D1. |
| D3 | DELETE /people/{lname} devolvía 200 + texto, el contrato dice 204 | **Código** (`people.delete` devuelve 204 sin cuerpo) | 204 *No Content* es lo habitual para un borrado exitoso, y así ya funcionaba DELETE de pizzas: con este cambio los dos borrados se comportan igual. El texto en inglés tampoco era JSON. |
| D4 | Los errores (400, 404, 406) no estaban documentados | **Contrato** | El código ya devolvía los errores correctos; faltaba declararlos. Se agregaron en `components/responses` (`BadRequest`, `PersonNotFound`, `PizzaNotFound`, `PersonAlreadyExists`) y se referencian con `$ref` en cada endpoint, para no repetir la misma descripción nueve veces. |
| D5 | POST /pizzas sin `content` daba 500 | **Contrato** (`content` obligatorio en POST y PUT; `requestBody` obligatorio) | El modelo ya exige `content` (`nullable=False`). Al declararlo en el contrato, Connexion rechaza la petición con 400 antes de llegar a la función, y el servidor ya no se rompe. |
| D6 | POST /pizzas sin `person_id` daba 404 | **Contrato** (`person_id` obligatorio en POST) | Si falta un dato obligatorio el error es del cliente y corresponde 400, no "persona no encontrada". |
| D7 | PUT /people exigía `lname` en el cuerpo y lo ignoraba | **Contrato** (nuevo esquema `PersonUpdate` que solo pide `fname`) y **código** (se asigna `fname` directamente) | El apellido identifica a la persona en la URL y no se puede cambiar por esta ruta. No tiene sentido obligar a mandarlo. Si se manda igual, se ignora como antes. |
| D8 | Esquemas incompletos, no había esquema Pizza | **Contrato** | Se definió `Pizza` en `components/schemas` (id, person_id, content, timestamp) y se reutiliza con `$ref` en todos los endpoints de pizzas y dentro de `Person.pizzas`. `Person` ahora describe también id, timestamp y pizzas. Los campos que genera el servidor (`id`, `timestamp`, `pizzas`) se marcaron `readOnly`: aparecen en las respuestas pero no se pueden mandar al crear (Connexion responde 400). |
| D13 | DELETE /pizzas armaba un texto que nunca se envía | **Código** | Una respuesta 204 no tiene cuerpo, así que el mensaje era código muerto. Ahora devuelve `make_response("", 204)`, igual que el borrado de personas. |

Diferencias que se resuelven en otras partes del TP: D9 (valores vacíos) y D11 (idioma de los
mensajes) en la Parte 5, y D10 (falta GET /api/pizzas) en la Parte 3.
D12 (`debug=True`): se mantiene durante el desarrollo porque reinicia el servidor solo al guardar
cambios, pero debe ir en `False` en un entorno real.

## Cómo se reutiliza el esquema Pizza

El POST necesita `person_id` y `content` obligatorios, pero el PUT solo `content`
(la pizza no cambia de dueño). Para reutilizar el mismo esquema sin duplicarlo se usa `allOf`:

```yaml
schema:
  x-body-name: "pizza"
  allOf:
    - $ref: "#/components/schemas/Pizza"   # los campos de la pizza
    - required:                              # y además, en este endpoint,
        - person_id                          # estos son obligatorios
        - content
```

## Cambios de código pedidos por la consigna

- `Pizza.query.get(id)` y `Person.query.get(id)` → `db.session.get(Pizza, id)` / `db.session.get(Person, id)`
  en `pizzas.py`. `Query.get()` es API heredada en SQLAlchemy 2.x.
- `datetime.utcnow` → `datetime.now(timezone.utc)` en `models.py`, a través de una función
  `ahora_utc()` que se pasa como `default` y `onupdate` de las columnas `timestamp`.
  `utcnow` está deprecado desde Python 3.12 porque devuelve una fecha sin zona horaria.
- En `update` se quitó `schema.load(...)` + `db.session.merge(...)`: el objeto ya está en la sesión,
  alcanza con asignar el campo y hacer `commit()`.

## Verificación (después de los cambios)

| Prueba | Antes | Ahora |
|--------|-------|-------|
| PUT /people/Corrente `{"fname":"Pablo Martin"}` | 201 | 200 |
| DELETE /people/Corrente | 200 + texto | 204 |
| POST /pizzas `{"person_id":2}` | 500 | 400 `'content' is a required property` |
| POST /pizzas `{"content":"Sin persona"}` | 404 | 400 `'person_id' is a required property` |
| PUT /pizzas/1 `{"content":"Pizza Napolitana"}` | 201 | 200 |
| PUT /pizzas/1 `{}` | 500 | 400 |
| Swagger UI | errores marcados *Undocumented* | todos los códigos documentados |
