from marshmallow import Schema, fields, ValidationError, validate


class CustomerSchema(Schema):
    id = fields.String(dump_only=True)
    user_id = fields.Integer()
    username = fields.String(validate=validate.Length(min=2))
    phone_number = fields.String(validate=validate.Length(min=8))
    address = fields.String(validate=validate.Length(min=5))
    first_name = fields.String(validate=validate.Length(min=3))
    surname = fields.String(validate=validate.Length(min=3))
    age = fields.Integer(validate=validate.Range(min=12, max=100))
    is_blocked = fields.Boolean()


class CategorySchema(Schema):
    id = fields.String(dump_only=True)
    title = fields.String(validate=validate.Length(min=3, max=512), required=True)
    slug = fields.String(validate=validate.Length(min=3, max=512), required=True)
    description = fields.String(validate=validate.Length(min=3, max=512))
    subcategories = fields.List(fields.Nested(lambda: CategorySchema(only=("id",))))
    parent = fields.Nested(lambda: CategorySchema(only=("id",)))


class Characteristics(Schema):
    height = fields.Integer()
    width = fields.Integer()
    weight = fields.Integer()


class ProductSchema(Schema):
    id = fields.String(dump_only=True)
    title = fields.String(required=True)
    slug = fields.String(required=True)
    description = fields.String(validate=validate.Length(min=3, max=512))
    price = fields.Integer(validate=validate.Range(min=0, max=10000), required=True)
    characteristics = fields.Nested(Characteristics)
    category = fields.String(validate=validate.Length(min=3, max=512))
    discount_percentage = fields.Integer(validate=validate.Range(min=0, max=100))
    image = fields.String(validate=validate.Length(min=3, max=512))
