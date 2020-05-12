from botshop.db.models import Customer, Product, Category, Characteristics
from mongoengine.errors import DoesNotExist
import datetime
import os
import requests
from requests.exceptions import MissingSchema


UPLOAD_FOLDER = f"{os.path.dirname(os.path.abspath(__file__))[:-3]}" + "db\product_images"


def update_customer(data, id):
    customer = Customer.objects.get(id=id)
    for key in data:
        customer[key] = data[key]
    customer.save()


def update_category(data, id):
    category = Category.objects.get(id=id)
    for key in data:
        category[key] = data[key]
    category.save()


def update_product(data, id):
    product = Product.objects.get(id=id)
    if data.get("category") is not None:
        new_category = Category.objects.get(id=data["category"])
        product.category = new_category
        del data["category"]
    if data.get('image'):
        product.image.delete()
        upload_image(data, update=True, product_obj=product)
        del data['image']
    if data.get('characteristics'):
        product.characteristics = Characteristics(**data.get('characteristics'))
        del data['characteristics']
    else:
        for key in data:
            product[key] = data[key]
    product.save()


def get_customer_by_id(id):
    try:
        return Customer.objects.get(id=id)
    except DoesNotExist:
        return False


def get_category_by_id(id):
    try:
        return Category.objects.get(id=id)
    except DoesNotExist:
        return False


def get_product_by_id(id):
    try:
        return Product.objects.get(id=id)
    except DoesNotExist:
        return False


def upload_image(data, update=False, product_obj=None):
    if update and product_obj:
        try:
            product = Product.objects(slug=data['slug']).first()
        except DoesNotExist as err:
            return str(err)
    product = product_obj
    try:
        content = requests.get(data['image']).content
    except MissingSchema as err:
        return str(err)
    count = datetime.datetime.now().microsecond
    filename = f'image_{count}.jpg'
    path_to_file = os.path.join(UPLOAD_FOLDER, filename)
    with open(path_to_file, 'wb') as file:
        file.write(content)
    with open(path_to_file, 'rb') as file_to_db:
        product.image.put(file_to_db, content_type='image/jpeg')
        product.save()


def create_product(data):
    t_data = {}
    for d in data:
        if not d == 'image':
            t_data[d] = data[d]
    Product.objects.create(**t_data)
