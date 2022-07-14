import sys
import logging

import requests
from telebot import TeleBot, logger
from telebot.types import Message, CallbackQuery
from pydantic import parse_obj_as

from settings import settings
from templates import get_home_keyboard, get_product_keyboard
from schemas import (
    Product,
    Shipping,
    Billing,
    LineItem,
    Order,
    CreateOrder,
    ShippingItem,
)


logger = logger
channel = logging.StreamHandler(sys.stdout)
logger.addHandler(channel)
logger.setLevel(logging.INFO)

bot = TeleBot(settings.telegram_token)


@bot.message_handler(commands=["start"])
def start_handler(message: Message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Добро пожаловать в магазин на вебинаре")
    bot.send_message(chat_id, "Выберите действие", reply_markup=get_home_keyboard())


@bot.message_handler(func=lambda m: m.text == "Каталог")
def catalog_handler(message: Message):
    chat_id = message.chat.id
    response = requests.get(
        f"{settings.api_host}/wp-json/wc/v2/products?per_page=10",
        auth=(settings.client_key, settings.client_secret),
    )
    products: list[Product] = parse_obj_as(list[Product], response.json())
    for product in products:
        bot.send_message(
            chat_id,
            f"Товар: #{product.id} {product.name} за {product.price} <a href='{product.images[0].src}'>&#8205;</a>",
            parse_mode="HTML",
            reply_markup=get_product_keyboard(product.id),
        )


@bot.callback_query_handler(func=lambda q: "order_" in q.data)
def order_handler(query: CallbackQuery):
    chat_id = query.message.chat.id
    product_id = query.data.split("_")[1]
    line_item = LineItem(product_id=product_id, quantity=1)
    shipping_item = ShippingItem(product_id=product_id, quantity=1)
    billing_info = Billing(
        first_name=query.from_user.first_name,
        last_name=query.from_user.last_name,
        address_1=query.from_user.id,
        city="San Francisco",
        country="US",
        email="john.doe@example.com",
        phone="(555) 555-5555",
    )
    shipping_info = Shipping(
        first_name=query.from_user.first_name,
        last_name=query.from_user.last_name,
        address_1=query.from_user.id,
        city="San Francisco",
        country="US",
        email="john.doe@example.com",
        phone="(555) 555-5555",
    )
    order = CreateOrder(
        billing=billing_info,
        shipping=shipping_info,
        line_items=[line_item],
        shipping_lines=[shipping_item],
    )
    response = requests.post(
        f"{settings.api_host}/wp-json/wc/v2/orders",
        data=order.json(),
        headers={"Content-type": "application/json"},
        auth=(settings.client_key, settings.client_secret),
    )
    message = ""
    if response.status_code == 201:
        created_order = Order.parse_obj(response.json())
        message = f"Ваш заказ успешно создан. Номер заказа {created_order.number}"
    else:
        message = "К сожалению ваш заказ провален"

    bot.send_message(chat_id, message)


bot.infinity_polling()
