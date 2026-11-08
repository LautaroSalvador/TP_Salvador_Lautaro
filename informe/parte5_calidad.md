# Parte 5 – Calidad: errores y pruebas automáticas (borrador para el informe)

## 1. Mensajes de error en español

Todos los mensajes que generan `people.py` y `pizzas.py` (con `abort`) quedaron en español.
Gracias a las funciones auxiliares de la Parte 3, cada mensaje está escrito en un solo lugar.

| Antes | Ahora | Código |
|-------|-------|--------|
| `Person with last name X not found` | `No existe una persona con apellido X` | 404 |
| `Person with last name X already exists` | `Ya existe una persona con apellido X` | 406 |
| `Person not found for ID: N` | `No existe una persona con ID N` | 404 |
| `Pizza with ID N not found` | `No existe una pizza con ID N` | 404 |

Limitación: los mensajes de **validación** (400) los genera Connexion al comparar la petición
con el contrato, antes de llegar a nuestro código (por ejemplo `'price' is a required property`).
Esos mensajes son de la librería y salen en inglés; traducirlos obligaría a reemplazar el validador
de Connexion. Se dejó así y se documenta acá.

## 2. Rechazar textos vacíos

Se resolvió en el **contrato** (contract first), en los esquemas `Person.lname` y `Pizza.content`:

```yaml
minLength: 1      # rechaza ""
pattern: "\\S"    # exige al menos un carácter que no sea espacio: rechaza "   "
```

`minLength` sola no alcanza, porque `"   "` (solo espacios) tiene largo 3. El patrón `\S`
("cualquier carácter que no sea un espacio") obliga a que haya al menos una letra.
Como `Pizza` se reutiliza con `$ref`, la regla vale para POST y PUT de pizzas.

| Petición | Respuesta |
|----------|-----------|
| POST /people `{"lname": ""}` | 400 `'' should be non-empty - 'lname'` |
| POST /people `{"lname": "   "}` | 400 |
| POST /pizzas con `"content": ""` | 400 `'' should be non-empty - 'content'` |

## 3. Pruebas automáticas con pytest

Archivo `tests/test_api.py`: **23 funciones de prueba (25 casos**, porque la del precio inválido
se repite con -500, 0 y "caro" usando `@pytest.mark.parametrize`).

**Cómo funcionan**
- Usan el cliente de pruebas de Flask (`flask_app.test_client()`), que manda peticiones HTTP
  a la API sin levantar el servidor.
- Una *fixture* (`client`) prepara cada prueba: crea una base nueva con los datos de ejemplo.
  Así cada prueba es independiente de las demás.
- La base de las pruebas es **en memoria** (`sqlite:///:memory:`): no se toca `people.db`.
  Para eso `config.py` ahora lee la variable de entorno `DATABASE_URL` (si no existe, usa
  `people.db` como siempre).
- `build_database.py` se reorganizó en una función `crear_base()` que usan tanto el script
  como las pruebas, para no duplicar la carga de datos.

**Casos que pide la consigna**

| Caso pedido | Prueba |
|-------------|--------|
| Listar personas | `test_listar_personas` |
| Crear persona | `test_crear_persona` |
| Apellido duplicado (406) | `test_crear_persona_con_apellido_duplicado_devuelve_406` |
| Persona inexistente (404) | `test_consultar_persona_inexistente_devuelve_404` |
| Crear pizza | `test_crear_pizza` |
| Pizza con persona inexistente | `test_crear_pizza_para_persona_inexistente_devuelve_404` |
| Precio inválido (400) | `test_crear_pizza_con_precio_invalido_devuelve_400` (-500, 0, "caro") |
| Borrado en cascada | `test_borrar_persona_borra_sus_pizzas_en_cascada` |
| GET /api/pizzas | `test_listar_todas_las_pizzas`, `test_listar_pizzas_filtrando_por_persona`, `test_listar_pizzas_de_persona_inexistente_por_id_devuelve_404` |
| GET /api/people/{lname}/pizzas | `test_listar_pizzas_de_una_persona`, `test_listar_pizzas_de_persona_inexistente_devuelve_404` |
| GET /api/people/{lname}/resumen | `test_resumen_de_persona`, `test_resumen_de_persona_inexistente_devuelve_404` |

**Pruebas adicionales**: apellido vacío, contenido vacío, pizza sin precio, tamaño inválido,
actualizar persona (200), actualizar pizza (200), borrar pizza (204), pizza inexistente (404).

**Resultado**: `25 passed` al terminar la Parte 5 (con las pruebas de paginación de la Parte 6, `34 passed`).

## 4. requirements.txt y README

- Se agregó `pytest>=8.0` a `requirements.txt`.
- `pytest.ini` le indica a pytest dónde están las pruebas y que la carpeta raíz es el proyecto
  (para que `import app` funcione), y oculta avisos internos de Connexion.
- `README.md` explica la instalación, cómo levantar la API, cómo correr las pruebas y la lista
  final de endpoints.
