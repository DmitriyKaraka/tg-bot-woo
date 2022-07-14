from telebot import types


def get_home_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(True)
    catalog_btn = types.KeyboardButton("Каталог")
    cart_btn = types.KeyboardButton("Корзина")
    home_btn = types.KeyboardButton("На главную")
    markup.row(catalog_btn, cart_btn)
    markup.row(home_btn)

    return markup


def get_product_keyboard(product_id: int) -> types.ReplyKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    order_btn = types.InlineKeyboardButton(
        "Заказать", callback_data=f"order_{product_id}"
    )
    markup.add(order_btn)
    return markup
