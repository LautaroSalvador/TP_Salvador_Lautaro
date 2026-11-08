from config import db
from flask import abort, make_response
from models import Person, people_schema, person_schema, pizzas_schema


def buscar_persona(lname):
    """Devuelve la persona con ese apellido, o corta con 404 si no existe."""
    person = Person.query.filter(Person.lname == lname).one_or_none()
    if person is None:
        abort(404, f"No existe una persona con apellido {lname}")
    return person


def read_all(limit=None, offset=0):
    # limit=None significa "sin límite": devuelve todas
    people = Person.query.order_by(Person.id).offset(offset).limit(limit).all()
    return people_schema.dump(people)


def create(person):
    lname = person.get("lname")
    existing_person = Person.query.filter(Person.lname == lname).one_or_none()

    if existing_person is None:
        new_person = person_schema.load(person, session=db.session)
        db.session.add(new_person)
        db.session.commit()
        return person_schema.dump(new_person), 201
    else:
        abort(406, f"Ya existe una persona con apellido {lname}")


def read_one(lname):
    person = buscar_persona(lname)
    return person_schema.dump(person)


def update(lname, person):
    existing_person = buscar_persona(lname)
    existing_person.fname = person.get("fname")
    db.session.commit()
    return person_schema.dump(existing_person), 200


def delete(lname):
    existing_person = buscar_persona(lname)
    db.session.delete(existing_person)
    db.session.commit()
    return make_response("", 204)


def read_pizzas(lname):
    person = buscar_persona(lname)
    return pizzas_schema.dump(person.pizzas)


def read_resumen(lname):
    person = buscar_persona(lname)
    return {
        "lname": person.lname,
        "fname": person.fname,
        "cantidad_pizzas": len(person.pizzas),
        "total_gastado": round(sum(pizza.price for pizza in person.pizzas), 2),
    }
