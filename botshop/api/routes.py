from flask import jsonify, request, render_template, Flask, abort, make_response
from botshop.api.utils import (update_customer,
                               update_category,
                               update_product,
                               get_customer_by_id,
                               get_category_by_id,
                               get_product_by_id,
                               upload_image,
                               create_product)
from botshop.db.models import Customer, Product, Category
from botshop.api.schemas import CustomerSchema, CategorySchema, ProductSchema

from mongoengine.errors import ValidationError as MongoValidationError, DoesNotExist
from marshmallow.exceptions import ValidationError as MarshmallowValidationError

from flask import Blueprint

app_rest = Blueprint('/botshop/api', __name__)


@app_rest.route('/customers', methods=['GET', 'POST'])
@app_rest.route('/customers/<string:customer_id>', methods=['GET', 'PUT', 'DELETE'])
def customers(customer_id=None):
    if customer_id:
        if request.method == 'GET':
            customer_data = get_customer_by_id(customer_id)  # obj

            if not customer_data:
                return jsonify({'message': 'user not found'}), 404
            else:
                return CustomerSchema().dump(customer_data)

        if request.method == 'PUT':
            try:
                data = CustomerSchema().load(request.get_json())
                update_customer(data, customer_id)
            except (MarshmallowValidationError, MongoValidationError) as error:
                abort(400, f"{error}")
            new_customer = Customer.objects(id=customer_id)
            return jsonify(CustomerSchema().dump(new_customer, many=True))

        if request.method == 'DELETE':
            try:
                Customer.objects.get(id=customer_id).delete()
            except (DoesNotExist, MongoValidationError) as error:
                abort(400, f"{error}")
            return make_response('', 204)
    else:
        if request.method == 'GET':
            customers = Customer.objects()
            return jsonify(CustomerSchema().dump(customers, many=True))

        if request.method == 'POST':  # works but need to test properly
            try:
                data = CustomerSchema().load(request.get_json())
            except MarshmallowValidationError as error:
                return str(error)
            customer = Customer.objects.create(**data)
            return CustomerSchema().dump(customer)


@app_rest.route('/categories', methods=['GET', 'POST'])
@app_rest.route('/categories/<string:category_id>', methods=['GET', 'PUT', 'DELETE'])
def categories(category_id=None):
    if category_id:
        if request.method == 'GET':
            category_data = get_category_by_id(category_id)  # obj

            if not category_data:
                return jsonify({'message': 'user not found'}), 404
            else:
                try:
                    return CategorySchema().dump(category_data)
                except TypeError as err:
                    return make_response(f'{err}', 500)

        if request.method == 'PUT':
            try:
                data = CategorySchema().load(request.get_json())
                update_category(data, category_id)
            except (MarshmallowValidationError, MongoValidationError) as error:
                abort(400, f"{error}")
            new_category = Category.objects(id=category_id)
            try:
                return jsonify(CategorySchema().dump(new_category, many=True))
            except TypeError as err:
                return make_response(f'{err}', 500)

        if request.method == 'DELETE':
            try:
                Category.objects.get(id=category_id).delete()
            except (DoesNotExist, MongoValidationError) as error:
                abort(400, f"{error}")
            return make_response('', 204)
    else:
        if request.method == 'GET':
            categories = Category.objects()
            try:
                return jsonify(CategorySchema().dump(categories, many=True))
            except TypeError as err:
                return make_response(f'{err}', 500)

        if request.method == 'POST':  # works but need to test properly
            try:
                data = CategorySchema().load(request.get_json())
            except MarshmallowValidationError as error:
                return str(error)
            category = Category.objects.create(**data)
            return CategorySchema().dump(category)


@app_rest.route('/products', methods=['GET', 'POST'])
@app_rest.route('/products/<string:product_id>', methods=['GET', 'PUT', 'DELETE'])
def products(product_id=None):
    if product_id:
        if request.method == 'GET':
            product_data = get_product_by_id(product_id)  # obj
            if not product_data:
                return jsonify({'message': 'user not found'}), 404
            else:
                return ProductSchema().dump(product_data)

        if request.method == 'PUT':
            try:
                data = ProductSchema().load(request.get_json())
                update_product(data, product_id)
            except (MarshmallowValidationError, MongoValidationError) as error:
                abort(400, f"{error}")
            new_product = Product.objects(id=product_id)
            return jsonify(ProductSchema().dump(new_product, many=True))

        if request.method == 'DELETE':
            try:
                Product.objects.get(id=product_id).delete()
            except (DoesNotExist, MongoValidationError) as error:
                abort(400, f"{error}")
            return make_response('', 204)
    else:
        if request.method == 'GET':
            products = Product.objects()
            return jsonify(ProductSchema().dump(products, many=True))

        if request.method == 'POST':  # works but need to test properly
            try:
                data = ProductSchema().load(request.get_json())
            except MarshmallowValidationError as error:
                return str(error)
            create_product(data)
            if data.get('image'):
                upload_image(data)
            product = Product.objects(slug=data['slug']).first()
            return ProductSchema().dump(product)


@app_rest.route('/hello')
def start():
    return 'hello'