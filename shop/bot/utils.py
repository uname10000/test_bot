import json

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from . import constants


def inline_kb_from_iterable(
        tag,
        iterable,
        id_field='id',
        text_field='title'
):
    buttons = []

    for i in iterable:
        json_data = json.dumps({
            id_field: str(getattr(i, id_field)),
            'tag': tag
        })

        buttons.append(
            InlineKeyboardButton(
                text=getattr(i, text_field),
                callback_data=json_data
            )
        )

    kb = InlineKeyboardMarkup()
    kb.add(*buttons)
    return kb


def is_start_button_pressed(message):
    if message.text == constants.START_KB[constants.CATEGORIES] \
        or message.text == constants.START_KB[constants.CART] \
        or message.text == constants.START_KB[constants.SETTINGS] \
        or message.text == constants.START_KB[constants.NEWS] \
        or message.text == constants.START_KB[constants.PRODUCTS_WITH_DISCOUNTS]:
        return True
    else:
        return False