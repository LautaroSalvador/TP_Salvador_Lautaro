from config import db
from flask import abort, make_response
from models import Pizza, Person, pizza_schema


def read_one(pizza_id):
    pizza = Pizza.query.get(pizza_id)

    if pizza is not None:
        return pizza_schema.dump(pizza)
    else:
        abort(404, f"Pizza with ID {pizza_id} not found")


def update(pizza_id, pizza):
    existing_pizza = Pizza.query.get(pizza_id)

    if existing_pizza:
        update_pizza = pizza_schema.load(pizza, session=db.session)
        existing_pizza.content = update_pizza.content
        db.session.merge(existing_pizza)
        db.session.commit()
        return pizza_schema.dump(existing_pizza), 201
    else:
        abort(404, f"Pizza with ID {pizza_id} not found")


def delete(pizza_id):
    existing_pizza = Pizza.query.get(pizza_id)

    if existing_pizza:
        db.session.delete(existing_pizza)
        db.session.commit()
        return make_response(f"{pizza_id} successfully deleted", 204)
    else:
        abort(404, f"Pizza with ID {pizza_id} not found")


def create(pizza):
    person_id = pizza.get("person_id")
    person = Person.query.get(person_id)

    if person:
        new_pizza = pizza_schema.load(pizza, session=db.session)
        person.pizzas.append(new_pizza)
        db.session.commit()
        return pizza_schema.dump(new_pizza), 201
    else:
        abort(404, f"Person not found for ID: {person_id}")
