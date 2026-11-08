# Parte 3 – Nuevos endpoints (borrador para el informe)

Se siguió el enfoque *contract first*: cada endpoint se declaró primero en `swagger.yml`
(ruta, parámetros, respuestas y errores) y después se implementó la función Python a la que
apunta su `operationId`.

## Resumen

| Endpoint | operationId | Respuesta | Errores |
|----------|-------------|-----------|---------|
| `GET /api/pizzas` | `pizzas.read_all` | 200, lista de `Pizza` | 404 si `person_id` no corresponde a ninguna persona; 400 si `person_id` no es un número |
| `GET /api/people/{lname}/pizzas` | `people.read_pizzas` | 200, lista de `Pizza` (de la más nueva a la más vieja) | 404 si la persona no existe |
| `GET /api/people/{lname}/resumen` | `people.read_resumen` | 200, objeto `Resumen` | 404 si la persona no existe |

## GET /api/pizzas

Lista todas las pizzas ordenadas por ID. Acepta el parámetro de consulta opcional `person_id`
(`/api/pizzas?person_id=2`), declarado en `components/parameters/person_id_query` con
`in: query` y `required: false`. Connexion pasa el valor como argumento de la función;
si no se manda, llega `None` y se devuelven todas.

```python
def read_all(person_id=None):
    if person_id is None:
        pizzas = Pizza.query.order_by(Pizza.id).all()
    else:
        pizzas = buscar_persona_por_id(person_id).pizzas
    return pizzas_schema.dump(pizzas)
```

## GET /api/people/{lname}/pizzas

Busca la persona por apellido y devuelve su lista `person.pizzas` (la relación 1 a N del modelo).

## GET /api/people/{lname}/resumen

Devuelve `lname`, `fname`, `cantidad_pizzas` (`len(person.pizzas)`) y `total_gastado`.
Se definió un esquema `Resumen` en `components/schemas`. En esta parte `total_gastado` vale 0
porque las pizzas todavía no tienen precio; se completa en la Parte 4.

## Mejora de código: búsqueda sin duplicación

Cada función repetía el mismo bloque "buscar la persona; si no existe, 404". Se extrajo a
funciones auxiliares:

- `people.buscar_persona(lname)`
- `pizzas.buscar_pizza(pizza_id)`
- `pizzas.buscar_persona_por_id(person_id)`

Como `abort()` corta la ejecución, cada endpoint queda en dos o tres líneas y el mensaje de
error se escribe en un solo lugar.

## Verificación

| Prueba | Resultado |
|--------|-----------|
| `GET /api/pizzas` | 200, las 7 pizzas |
| `GET /api/pizzas?person_id=2` | 200, las 2 pizzas de Gomez |
| `GET /api/pizzas?person_id=99` | 404 |
| `GET /api/people/Lopez/pizzas` | 200, 2 pizzas |
| `GET /api/people/NoExiste/pizzas` | 404 |
| `GET /api/people/Sanchez/resumen` | 200, `cantidad_pizzas: 3` |
| `GET /api/people/NoExiste/resumen` | 404 |
