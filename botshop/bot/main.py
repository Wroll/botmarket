from .webshopbot import WebShopBot
from .configs import TOKEN
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telebot.apihelper import ApiException
from .keyboard import START_KB
from flask import Flask, request, abort, Blueprint
from botshop.db.models import Category, News, Product, Customer, CartItem, Cart
from timeloop import Timeloop
from datetime import timedelta

tl = Timeloop()

bot = WebShopBot(TOKEN)

bot_app = Blueprint('/botshop/bot', __name__)


@bot_app.route('/', methods=['POST'])
def process_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(status=403)


@bot.message_handler(commands=['start'])
def start(message):
    bot.check_basket_customer(message)
    buttons = [KeyboardButton(value) for value in START_KB.values()]
    bot.start(buttons, chat_id=message.chat.id)
    bot.send_categories(chat_id=message.chat.id)


@bot.message_handler(func=lambda message: message.text == START_KB["categories"])
def categories(message):
    bot.send_categories(message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('category'))
def category_handler(call):
    category_id = "".join(call.data.split("_")[1::])
    category = Category.objects.get(id=category_id)
    if category.subcategories:
        bot.send_subcategories(call, category)

    elif category.is_leaf:
        bot.send_products(call, category)


@bot.callback_query_handler(func=lambda call: call.data.startswith('back'))
def back_to_categories(call):
    bot.send_categories(call.message.chat.id, message_id=call.message.message_id, back_to_categories=True)


@bot.message_handler(func=lambda message: message.text == START_KB["news"])
def get_news(message):
    bot.send_news(message.chat.id)


@bot.message_handler(func=lambda message: message.text == START_KB["dis_products"])
def get_discount_products(message):
    bot.send_discount_products(message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('product'))
def put_product_into_basket(call):
    product = "".join(call.data.split("_")[1::])
    bot.put_product(call, product)


@bot.message_handler(func=lambda message: message.text == START_KB["basket"])
def user_basket_handler(message):
    customer = Customer.objects.get(user_id=message.chat.id).id
    customer_basket = Cart.objects.get(customer=customer, is_archive=False)
    bot.view_basket(message, customer_basket)


@bot.callback_query_handler(func=lambda call: call.data.startswith('remove'))
def remove_item_from_basket(call):
    product = "".join(call.data.split("_")[1::])
    bot.remove_item(call, product)


@bot.callback_query_handler(func=lambda call: call.data.startswith('order'))
def order_user_basket(call):
    bot.order_basket(call)


@tl.job(interval=timedelta(hours=168))
def cron_task():
    customers = Customer.objects()
    chat_id_customers = [i.user_id for i in customers]
    for chat_id_user in chat_id_customers:
        try:
            bot.send_chat_action(
                chat_id_user,
                action="typing")
        except ApiException:
            customer = Customer.objects.get(user_id=chat_id_user)
            customer.is_blocked = True
            customer.save()


def set_webhook():
    import time
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(
        url="https://34.77.22.214/tg ",
        certificate=open("botshop/bot/webhook_cert.pem", 'r'))


tl.start()
