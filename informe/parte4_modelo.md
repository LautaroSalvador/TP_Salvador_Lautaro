# Parte 4 – Modelo extendido: precio y tamaño (borrador para el informe)

## Campos nuevos de Pizza

| Campo | Tipo | Reglas | Dónde se valida |
|-------|------|--------|-----------------|
| `price` | número | obligatorio, mayor que 0 | contrato: `minimum: 0` + `exclusiveMinimum: true` y `required`; base: `nullable=False` |
| `size` | texto | solo `chica`, `mediana` o `grande` | contrato: `enum` |

Decisión: la consigna pide `price` obligatorio pero no dice lo mismo de `size`, así que `size`
quedó **opcional** (si no se manda, se guarda vacío / `null`). Si se manda, tiene que ser uno de los
tres valores permitidos. Todas las pizzas de ejemplo tienen tamaño.

## Cambios por archivo

**models.py**: dos columnas nuevas en `Pizza`:

```python
price = db.Column(db.Float, nullable=False)
size = db.Column(db.String(10))
```

`PizzaSchema` (Marshmallow) se genera solo a partir del modelo, así que incluye los campos nuevos
sin tocarlo.

**swagger.yml**: en el esquema `Pizza`:

```yaml
price:
  type: "number"
  minimum: 0
  exclusiveMinimum: true    # estrictamente mayor que 0: el 0 también se rechaza
size:
  type: "string"
  enum: ["chica", "mediana", "grande"]
```

`price` se agregó a la lista `required` del POST y del PUT. Como el esquema `Pizza` se reutiliza
con `$ref` (Parte 2), el cambio aparece automáticamente en todos los endpoints de pizzas.

**pizzas.py**:
- `create`: no hubo que cambiarlo. `pizza_schema.load(...)` toma todos los campos del JSON,
  incluidos `price` y `size`.
- `update`: además de `content`, ahora asigna `price` y `size`. El PUT reemplaza la pizza completa:
  si no se manda `size`, queda vacío.

**people.py**: el resumen ahora calcula el total real:

```python
"total_gastado": round(sum(pizza.price for pizza in person.pizzas), 2)
```

**build_database.py**: cada pizza de ejemplo es `(contenido, precio, tamaño, fecha)`.
Errores de tipeo corregidos:

| Antes | Después |
|-------|---------|
| Pizza roqefort | Pizza Roquefort |
| Piza Cuatro Quesos | Pizza Cuatro Quesos |
| Pizza Peperoni | Pizza Pepperoni |
| Pizza de Jamon crudo y Rucula | Pizza de Jamón crudo y Rúcula |

**templates/home.html**: muestra el tamaño, el precio y la fecha de cada pizza.

Importante: como cambió la estructura de la tabla, hay que volver a correr
`python build_database.py` (la base vieja no tiene las columnas nuevas).

## Verificación: precio negativo o tamaño inválido → 400

| Petición | Código | Mensaje |
|----------|--------|---------|
| POST `{"person_id":2,"content":"Pizza Fugazzeta","price":9800,"size":"mediana"}` | 201 | pizza creada |
| POST con `"price": -500` | 400 | `-500 is less than or equal to the minimum of 0 - 'price'` |
| POST con `"price": 0` | 400 | `0 is less than or equal to the minimum of 0 - 'price'` |
| POST con `"size": "gigante"` | 400 | `'gigante' is not one of ['chica', 'mediana', 'grande'] - 'size'` |
| POST sin `price` | 400 | `'price' is a required property` |
| POST con `"price": "caro"` | 400 | `'caro' is not of type 'number' - 'price'` |
| PUT /pizzas/1 con `"price": -1` | 400 | rechazado |
| GET /people/Sanchez/resumen | 200 | `total_gastado: 29200.0` (9500 + 8200 + 10800, datos recién cargados) |

Estas validaciones las hace **Connexion** comparando el JSON con el contrato, antes de llamar a
la función de Python: no hizo falta escribir ningún `if` para validar precio o tamaño.
