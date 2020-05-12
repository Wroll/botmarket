from telebot import TeleBot
from telebot.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from typing import List
from botshop.db.models import Category, News, Product, Customer, Texts, Cart, CartItem


class WebShopBot(TeleBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def start(self, buttons: List[KeyboardButton], text: str = None, force_send=True, chat_id: int = None):
        if not text:
            text = Texts.choices[0][0]
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(*buttons)
        if all([force_send, chat_id, text]):
            self.send_message(
                chat_id,
                text,
                reply_markup=kb)

        else:
            return kb

    @classmethod
    def check_basket_customer(cls, message):
        user = Customer.objects(user_id=message.chat.id).first()
        if not user:
            user_data = {'user_id': message.chat.id,
                         'username': message.chat.username,
                         'first_name': message.chat.first_name,
                         'surname': message.chat.last_name,
                         }
            Customer(**user_data).save()
            user = Customer.objects.get(user_id=message.chat.id)
        user.get_or_create_current_cart()

    def send_categories(self, chat_id: int, back_to_categories=False, message_id=None):
        kb = InlineKeyboardMarkup(row_width=2)
        categories = Category.get_root()
        buttons = [InlineKeyboardButton(text=category.title, callback_data=f'category_{category.id}') for category in
                   categories]
        kb.add(*buttons)
        if back_to_categories and message_id:
            self.edit_message_text(
                text="Choose category",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=kb)
        else:
            self.send_message(
                chat_id,
                text="Here is available categories",
                reply_markup=kb
            )

    def send_subcategories(self, call_data, category):
        categories = category.subcategories
        buttons = [InlineKeyboardButton(text=category.title, callback_data=f'category_{category.id}') for category in
                   categories]
        buttons.append(InlineKeyboardButton(text="back to categories", callback_data="back"))
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(*buttons)
        self.edit_message_text(
            category.title,
            chat_id=call_data.message.chat.id,
            message_id=call_data.message.message_id,
            reply_markup=kb)

    def send_products(self, call_data, category):
        kb = InlineKeyboardMarkup(row_width=2)
        for product in category.products:
            button = InlineKeyboardButton(text="To basket", callback_data=f"product_{product.id}")
            kb.keyboard = [[button.to_dic()]]
            if product.image:
                self.send_photo(
                    call_data.message.chat.id,
                    product.image.read(),
                    caption=f"title : {product.title}\n"
                            f"description : {product.description}\n"
                            f"price : {product.price}\n",
                    disable_notification=True,
                    reply_markup=kb)

            else:
                self.send_message(
                    call_data.message.chat.id,
                    text=f"title : {product.title}\n"
                         f"description : {product.description}\n"
                         f"price : {product.price}\n",
                    reply_markup=kb)

    def send_news(self, chat_id):
        news = News.objects()
        for n in news:
            self.send_message(
                chat_id,
                f"Title: {n.title}\n"
                f"Body of post: {n.body}\n"
                f"Date: {n.pub_date}")

    def send_discount_products(self, chat_id):
        kb = InlineKeyboardMarkup(row_width=2)
        products = Product.get_discount_products()
        for product in products:
            button = InlineKeyboardButton(text="To basket", callback_data=f"product_{product.id}")
            kb.keyboard = [[button.to_dic()]]
            if product.image:
                self.send_photo(
                    chat_id,
                    product.image.read(),
                    caption=f"title : {product.title}\n"
                            f"description : {product.description}\n"
                            f"price : {product.price}\n",
                    disable_notification=True,
                    reply_markup=kb)
            else:
                self.send_message(
                    chat_id,
                    text=f"title : {product.title}\n"
                         f"description : {product.description}\n"
                         f"price : {product.price}\n",
                    reply_markup=kb)

    def available_categories(self, message):
        self.send_message(
            message.chat.id,
            Texts.choices[0][0]
        )

        button = InlineKeyboardMarkup()
        categories = Category.get_all_categories()  # ['phones', 'laptops']
        buttons = []
        for category_name in categories:
            buttons.append(InlineKeyboardButton(text=category_name, callback_data=category_name))
        button.add(*buttons)
        self.send_message(message.chat.id, "Here is all available categories in our market\n",
                          reply_markup=button)

    def put_product(self, call, product):
        customer = Customer.objects.get(user_id=call.message.chat.id).id
        customer_basket = Cart.objects.get(customer=customer, is_archive=False)
        customer_basket.add_item(CartItem(product=product))
        self.send_message(
            call.message.chat.id,
            text=f"Product {Product.objects.get(id=product).title}, added to basket", )

    def view_basket(self, message, basket):
        amount_of_items = 0
        total_price = 0
        kb = InlineKeyboardMarkup(row_width=2)
        kb_order = InlineKeyboardMarkup(row_width=2)
        button_order = [InlineKeyboardButton(text="Order", callback_data=f"order_{basket}")]
        kb_order.add(*button_order)
        if basket.amount_items() == 0:
            self.send_message(
                message.chat.id,
                text="Your basket is empty"
            )
        else:
            for cart_item in basket.cart_items:
                amount_of_items += cart_item.quantity
                total_price += cart_item.price
                button = InlineKeyboardButton(text="Remove", callback_data=f"remove_{cart_item.product.id}")
                kb.keyboard = [[button.to_dic()]]
                if cart_item.product.image:
                    self.send_photo(
                        message.chat.id,
                        cart_item.product.image.read(),
                        caption=f"title : {cart_item.product.title}\n"
                                f"description : {cart_item.product.description}\n"
                                f"price : {cart_item.product.price}\n",
                        disable_notification=True,
                        reply_markup=kb)
                else:
                    self.send_message(
                        message.chat.id,
                        text=f"title : {cart_item.product.title}\n"
                             f"description : {cart_item.product.description}\n"
                             f"price : {cart_item.product.price}\n",
                        reply_markup=kb)

            self.send_message(
                message.chat.id,
                f"Total items in your basket is: {amount_of_items}\n"
                f"Total price is: {total_price}\n",
                reply_markup=kb_order,
            )

    def remove_item(self, call, item):
        customer = Customer.objects.get(user_id=call.message.chat.id).id
        customer_basket = Cart.objects.get(customer=customer, is_archive=False)
        customer_basket.remove_item(item)
        self.send_message(
            call.message.chat.id,
            text=f"{Product.objects.get(id=item).title} removed"
        )

    def order_basket(self, call):
        customer = Customer.objects.get(user_id=call.message.chat.id).id
        customer_basket = Cart.objects.get(customer=customer, is_archive=False)
        customer_basket.archive()
        self.check_basket_customer(call.message)
        self.send_message(
            call.message.chat.id,
            text="order in process"
        )
