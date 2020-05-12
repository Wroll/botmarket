import mongoengine as me
import datetime
from slugify import slugify
from typing import Tuple
from mongoengine.errors import DoesNotExist

me.connect('SHOP_DB')


class Customer(me.Document):
    user_id = me.IntField(unique=True)
    username = me.StringField(min_length=1, max_length=256)
    phone_number = me.StringField(min_length=8)
    address = me.StringField()
    first_name = me.StringField(min_length=1, max_length=256)
    surname = me.StringField(min_length=1, max_length=256)
    age = me.IntField(min_value=12, max_value=99)
    is_blocked = me.BooleanField(default=False)

    def get_or_create_current_cart(self) -> Tuple[bool, 'Cart']:
        created = False
        cart = Cart.objects(customer=self, is_archive=False)
        if cart:
            return created, cart
        else:
            return Cart.objects.create(customer=self)

    def get_history(self):
        pass


class Characteristics(me.EmbeddedDocument):
    height = me.IntField()
    width = me.IntField()
    weight = me.IntField()


class Category(me.Document):
    title = me.StringField(min_length=2, max_length=512, required=True)
    slug = me.StringField(min_length=2, max_length=512, unique=True, required=True)
    description = me.StringField(min_length=2, max_length=2048)
    subcategories = me.ListField(me.ReferenceField('self'))
    parent = me.ReferenceField('self')

    def set_slug(self, slug_from_admin=None):
        if slug_from_admin is None or self.slug is None:
            self.slug = slugify(self.title)
        else:
            self.slug = slugify(slug_from_admin)
        self.save()

    @classmethod
    def get_root(cls):
        return cls.objects(parent=None)

    @staticmethod
    def get_all_categories():
        category_names = []
        objs = Category.objects()
        for c in objs:
            category_names.append(c.title)
        return category_names

    def add_subcategory(self, subcategory_obj):
        subcategory_obj.parent = self
        self.subcategories.append(subcategory_obj.save())
        self.save()

    @property
    def products(self):
        return Product.objects(category=self)

    @property
    def is_root(self):
        return self.parent is None

    @property
    def is_leaf(self):
        return not self.subcategories


class Product(me.Document):
    title = me.StringField(min_length=2, max_length=512, required=True)
    slug = me.StringField(min_length=2, max_length=512, unique=True, required=True)
    description = me.StringField(min_length=2, max_length=2048)
    price = me.IntField(min_value=1, force_string=True, required=True)
    characteristics = me.EmbeddedDocumentField(Characteristics)
    category = me.ReferenceField(Category)
    discount_percentage = me.IntField(min_value=0, max_value=100)
    image = me.FileField()

    @classmethod
    def get_discount_products(cls):
        return cls.objects(discount_percentage__gt=0)

    def get_price(self):
        percentage = 100 - self.discount_percentage
        return self.price * percentage / 100


class News(me.Document):
    title = me.StringField(min_length=2, max_length=512)
    body = me.StringField(min_length=10, max_length=4096)
    pub_date = me.DateTimeField(default=datetime.datetime.now())


class Texts(me.Document):
    choices = (
        ('Greeting', 'Greeting'),
        ('Buy', 'Buy')
    )
    text = me.StringField(choices=choices)

    def __str__(self):
        return f"{self.choices}"


class CartItem(me.EmbeddedDocument):
    product = me.ReferenceField('Product')
    quantity = me.IntField(min_value=1, default=1, max_value=20)

    @property
    def price(self):
        return self.product.price * self.quantity


class Cart(me.Document):
    customer = me.ReferenceField(Customer)
    cart_items = me.EmbeddedDocumentListField(CartItem)
    is_archive = me.BooleanField(default=False)

    def add_item(self, item: Product):
        if item in self.cart_items:
            self.cart_items[self.cart_items.index(item)].quantity += 1
        else:
            self.cart_items.append(item)
        self.save()

    def remove_item(self, item_id: Product):
        product_to_delete = Product.objects.get(id=item_id)
        for item in self.cart_items:  # TODO make without loop
            if item.product == product_to_delete:
                if item.quantity == 1:
                    self.cart_items.remove(item)
                else:
                    self.cart_items[self.cart_items.index(item)].quantity -= 1
        self.save()

    def amount_items(self):
        return len(self.cart_items)

    def archive(self):
        self.is_archive = True
        self.save()
