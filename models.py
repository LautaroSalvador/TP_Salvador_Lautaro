from datetime import datetime, timezone

from config import db, ma
from marshmallow_sqlalchemy import fields


def ahora_utc():
    """Fecha y hora actual en UTC (reemplaza a datetime.utcnow, deprecado desde Python 3.12)."""
    return datetime.now(timezone.utc)


class Pizza(db.Model):
    __tablename__ = "pizza"
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"))
    content = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    size = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=ahora_utc, onupdate=ahora_utc)


class PizzaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Pizza
        load_instance = True
        sqla_session = db.session
        include_fk = True


class Person(db.Model):
    __tablename__ = "person"
    id = db.Column(db.Integer, primary_key=True)
    lname = db.Column(db.String(32), unique=True)
    fname = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime, default=ahora_utc, onupdate=ahora_utc)

    pizzas = db.relationship(
        Pizza,
        backref="person",
        cascade="all, delete, delete-orphan",
        single_parent=True,
        order_by="desc(Pizza.timestamp)",
    )


class PersonSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    pizzas = fields.Nested(PizzaSchema, many=True)


pizza_schema = PizzaSchema()
pizzas_schema = PizzaSchema(many=True)
person_schema = PersonSchema()
people_schema = PersonSchema(many=True)
