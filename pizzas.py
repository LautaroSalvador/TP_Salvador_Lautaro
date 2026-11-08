from config import db
from flask import abort, make_response
from models import Pizza, Person, pizza_schema, pizzas_schema


def buscar_pizza(pizza_id):
    """Devuelve la pizza con ese ID, o corta con 404 si no existe."""
    pizza = db.session.get(Pizza, pizza_id)
    if pizza is None:
        abort(404, f"No existe una pizza con ID {pizza_id}")
    return pizza


def buscar_persona_por_id(person_id):
    """Devuelve la persona con ese ID, o corta con 404 si no existe."""
    person = db.session.get(Person, person_id)
    if person is None:
        abort(404, f"No existe una persona con ID {person_id}")
    return person


def read_all(person_id=None, limit=None, offset=0):
    consulta = Pizza.query.order_by(Pizza.id)
    if person_id is not None:
        buscar_persona_por_id(person_id)  # 404 si la persona no existe
        consulta = consulta.filter(Pizza.person_id == person_id)
    # limit=None significa "sin límite": devuelve todas
    pizzas = consulta.offset(offset).limit(limit).all()
    return pizzas_schema.dump(pizzas)


def read_one(pizza_id):
    pizza = buscar_pizza(pizza_id)
    return pizza_schema.dump(pizza)


def update(pizza_id, pizza):
    existing_pizza = buscar_pizza(pizza_id)
    existing_pizza.content = pizza.get("content")
    existing_pizza.price = pizza.get("price")
    existing_pizza.size = pizza.get("size")
    db.session.commit()
    return pizza_schema.dump(existing_pizza), 200


def delete(pizza_id):
    existing_pizza = buscar_pizza(pizza_id)
    db.session.delete(existing_pizza)
    db.session.commit()
    return make_response("", 204)


def create(pizza):
    person = buscar_persona_por_id(pizza.get("person_id"))
    new_pizza = pizza_schema.load(pizza, session=db.session)
    person.pizzas.append(new_pizza)
    db.session.commit()
    return pizza_schema.dump(new_pizza), 201
