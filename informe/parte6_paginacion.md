# Parte 6 (opcional) – Paginación (borrador para el informe)

Opción elegida: **paginación**. `GET /api/people` y `GET /api/pizzas` aceptan los parámetros
de consulta opcionales `limit` y `offset`.

## Qué es

Cuando una lista crece, no conviene devolverla entera. Con paginación el cliente pide "una página":

- `limit`: cuántos resultados querés como máximo.
- `offset`: cuántos saltear desde el principio.

Ejemplo con 7 pizzas y páginas de 3: `?limit=3&offset=0` → pizzas 1-3, `?limit=3&offset=3` → 4-6,
`?limit=3&offset=6` → 7.

## Contrato (swagger.yml)

Se declararon una sola vez en `components/parameters` y se referencian con `$ref` en los dos
endpoints:

```yaml
limit:
  name: "limit"
  in: query
  required: false
  schema:
    type: "integer"
    minimum: 1
offset:
  name: "offset"
  in: query
  required: false
  schema:
    type: "integer"
    minimum: 0
    default: 0
```

Connexion valida los valores: `limit=0`, `offset=-1` o `limit=abc` devuelven 400 sin llegar al código.
Se agregó la respuesta 400 a la documentación de ambos endpoints.

## Código

SQLAlchemy ya tiene `.offset()` y `.limit()`, que se traducen a `OFFSET` y `LIMIT` en SQL.
La base devuelve solo la página pedida, no hace falta traer todo y recortar en Python.

```python
def read_all(limit=None, offset=0):
    people = Person.query.order_by(Person.id).offset(offset).limit(limit).all()
    return people_schema.dump(people)
```

- `order_by(Person.id)`: sin un orden fijo, la base podría devolver los registros en distinto
  orden en cada consulta y las páginas se superpondrían.
- `limit=None` le indica a SQLAlchemy que no ponga límite. Por eso, si no se manda `limit`,
  el endpoint se comporta igual que antes (devuelve todo): el cambio es compatible.

En `pizzas.read_all` se reescribió el filtro por persona como una consulta (`filter`) en lugar de
usar la lista `person.pizzas`, para poder combinar filtro y paginación:
`/api/pizzas?person_id=1&limit=2&offset=1`.

## Pruebas agregadas

| Prueba | Verifica |
|--------|----------|
| `test_paginar_personas_con_limit` | `?limit=2` → Sanchez, Gomez |
| `test_paginar_personas_con_limit_y_offset` | `?limit=2&offset=2` → Lopez |
| `test_paginar_pizzas_con_limit_y_offset` | `?limit=3&offset=3` → pizzas 4, 5, 6 |
| `test_paginar_pizzas_de_una_persona` | `?person_id=1&limit=2&offset=1` → pizzas 2, 3 |
| `test_offset_mayor_que_la_cantidad_devuelve_lista_vacia` | `?offset=100` → `[]` |
| `test_paginacion_con_valores_invalidos_devuelve_400` | `limit=0`, `limit=-1`, `offset=-1`, `limit=abc` → 400 en los dos endpoints |

Resultado total: **34 passed**.
