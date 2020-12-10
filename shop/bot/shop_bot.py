import json

from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from ..models.shop_models import Category
from ..models.extra_models import News
from .config import TOKEN
from .utils import inline_kb_from_iterable
from . import constants

# botname: Shptestbot
# bot username: Shptest_bot
bot = TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def handle_start(message):
    # print('start handler')
    name = f' {message.from_user.first_name}' if getattr(message.from_user, 'first_name') else ''
    greetings = constants.GREETINGS.format(name)

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [KeyboardButton(n) for n in constants.START_KB.values()]
    kb.add(*buttons)

    bot.send_message(message.chat.id, greetings, reply_markup=kb)


@bot.message_handler(func=lambda m: constants.START_KB[constants.CATEGORIES] == m.text)
def handle_messages(message):
    print('message handler categories')
    # kb = InlineKeyboardButton()
    root_categories = Category.get_root_categories()

    # buttons = []
    #
    # for c in root_categories:
    #     json_data = json.dumps({
    #         'id': str(c.id),
    #         'tag': 'category',
    #     })
    #     button = InlineKeyboardButton(
    #         text=c.title,
    #         callback_data=json_data
    #     )
    #
    #     buttons.append(button)
    #
    # kb.add(*buttons)

    kb = inline_kb_from_iterable(constants.CATEGORY_TAG, root_categories)

    bot.send_message(
        message.chat.id,
        'Выберете категорию',
        reply_markup=kb
    )


@bot.message_handler(func=lambda m: constants.START_KB[constants.CART] == m.text)
def handler_message_cart(message):
    print('handler message cart')


@bot.message_handler(func=lambda m: constants.START_KB[constants.SETTINGS] == m.text)
def handler_message_settings(message):
    print('handler message settings')


@bot.message_handler(func=lambda m: constants.START_KB[constants.NEWS] == m.text)
def handler_message_news(message):
    print('handler message news')
    news = News.objects()
    sorted_news = []

    print(news[0].creation_time.created_time.time())
    print(news[1].creation_time.created_time.replace(microsecond=0))

    if news[0].creation_time.created_time.replace(microsecond=0) < news[1].creation_time.created_time.replace(microsecond=0):
        print(f'{news[0].creation_time.created_time} < {news[1].creation_time.created_time}')
    else:
        print(f'{news[0].creation_time.created_time} > {news[1].creation_time.created_time}')
    bot.send_message(
        message.chat.id,
        'message 1'
    )

    bot.send_message(
        message.chat.id,
        'message 2'
    )


@bot.message_handler(func=lambda m: constants.START_KB[constants.PRODUCTS_WITH_DISCOUNTS] == m.text)
def handler_message_prod_with_disc(message):
    print('handler message prod with dics')


@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants.CATEGORY_TAG)
def handler_category_click(call):
    print(call)


@bot.message_handler(content_types=['text'])
def handler_test(message):
    print('handler text')