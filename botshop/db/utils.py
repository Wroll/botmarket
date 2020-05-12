from botshop.db.models import Category, Product, News, Customer, Characteristics
import random
from slugify import slugify
from faker import Faker
import os
import datetime

fake = Faker()


class GeneratorHandler:
    @staticmethod
    def attach_image_to_product(product_id: str):
        product = Product.objects(id=product_id).first()
        if product is None:
            print(f"No product with id : {product_id}")
            return False
        path = f"{os.path.dirname(os.path.abspath(__file__))}" + "\product_images" + f"\{random.randint(1, 10)}.jpg"
        with open(path, 'rb') as file:
            product.image.put(file, content_type='image/jpeg')
            product.save()

    @staticmethod
    def create_category():
        title = random.choice(Data.category_titles + Data.product_titles)
        slug = slugify(title + str(datetime.datetime.now().microsecond))
        data = {'title': title,
                'slug': slug,
                'description': fake.sentence(),
                }
        Category(**data).save()
        return Category.objects.get(slug=slug)

    @staticmethod
    def create_subcategory(category: Category):
        title = random.choice(Data.category_titles + Data.product_titles)
        slug = slugify(title + str(datetime.datetime.now().microsecond))
        data = {'title': title,
                'slug': slug,
                'description': fake.text(),
                }
        Category(**data).save()
        subcategory = Category.objects.get(slug=slug)
        category.add_subcategory(subcategory)
        return subcategory

    @staticmethod
    def create_product(category: Category):
        title = random.choice(Data.product_titles)
        slug = slugify(title + str(datetime.datetime.now().microsecond))
        data = {'title': title,
                'slug': slug,
                'description': fake.text(),
                'price': float(random.randint(50, 200)),
                'characteristics': Characteristics(height=float(random.randint(10, 50)),
                                                   width=float(random.randint(10, 50)),
                                                   weight=float(random.randint(10, 50))),
                'category': category,
                'discount_percentage': random.randint(10, 90), }
        Product(**data).save()
        GeneratorHandler.attach_image_to_product(Product.objects.get(slug=slug).id)

    @staticmethod
    def create_customer():
        test_data = {
            'username': fake.name(),
            'phone_number': fake.phone_number(),
            'address': fake.address(),
            'first_name': fake.first_name(),
            'surname': fake.last_name(),
            'age': random.randint(18, 50)
        }
        Customer(**test_data).save()

    @staticmethod
    def create_news():
        data = {
            'title': random.choice(Data.titles),
            'body': fake.text()
        }
        News.objects.create(**data)


class Data:
    titles = ['black friday', 'huge discounts', 'New year discounts', 'Summer discounts', 'Happy discounts']
    category_titles = ["Apple Smartphones & Phones",
                       "Laptops and computers",
                       "Gadgets",
                       "Tablets and e-books",
                       "Photo, Video, Audio",
                       "TV projectors",
                       "Appliances",
                       "Game Zone",
                       "Electronics Accessories",
                       "Home and Car",
                       "Tools and gardening equipment"]
    product_titles = [
        "Washing and drying machine",
        "Refrigerator",
        "Freezer"
        "Dishwasher",
        "CookersHood",
        "Cooking surface",
        "Hood",
        "Oven",
        "Hood accessorie",
        "Built- in appliance",
        "Washing machine",
        "Coffee maker",
        "Heater",
        "Air conditioning",
        "Moisturizer",
        "Air purifier",
        "Boiler",
        "Column",
    ]

