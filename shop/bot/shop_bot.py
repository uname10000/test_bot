import json

from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Message
from mongoengine import NotUniqueError

from ..models.shop_models import Category, User, Product
from ..models.extra_models import News
from .config import TOKEN
from .utils import inline_kb_from_iterable
from . import constants

# botname: Shptestbot
# bot username: Shptest_bot
bot = TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        User.objects.create(
            telegram_id=message.chat.id,
            username=getattr(message.from_user, 'username', None),
            first_name=getattr(message.from_user, 'first_name', None)
        )
    except NotUniqueError:
        greetings = 'Рады снова тебя видеть'
    else:
        name = f' {message.from_user.first_name}' if getattr(message.from_user, 'first_name') else ''
        greetings = constants.GREETINGS.format(name)

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [KeyboardButton(n) for n in constants.START_KB.values()]
    kb.add(*buttons)

    bot.send_message(message.chat.id, greetings, reply_markup=kb)


@bot.message_handler(func=lambda m: constants.START_KB[constants.CATEGORIES] == m.text)
def handle_messages(message: Message):
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


@bot.message_handler(func=lambda m: constants.START_KB[constants.SETTINGS] == m.text)
def handler_settings(message):
    user = User.objects.get(telegram_id=message.chat.id)
    bot.send_message(
        message.chat.id,
        user.formated_data()
    )


@bot.message_handler(func=lambda m: constants.START_KB[constants.CART] == m.text)
def handler_message_cart(message):
    print('handler message cart')


@bot.message_handler(func=lambda m: constants.START_KB[constants.SETTINGS] == m.text)
def handler_message_settings(message):
    print('handler message settings')


@bot.message_handler(func=lambda m: constants.START_KB[constants.NEWS] == m.text)
def handler_message_news(message):
    # print('handler message news')
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
    category = Category.objects.get(
        id=json.loads(call.data)['id']
    )

    if category.subcategories:
        kb = inline_kb_from_iterable(constants.CATEGORY_TAG, category.subcategories)
        bot.edit_message_text(
            category.title,
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            reply_markup=kb
        )
        # bot.send_message(
        #     call.message.chat.id,
        #     category.title,
        #     reply_markup=kb
        # )
    else:
        products = category.get_products()
        for p in products:
            kb = InlineKeyboardMarkup()
            button = InlineKeyboardButton(
                text=constants.ADD_TO_CART,
                callback_data=json.dumps(
                    {
                        'id': str(p.id),
                        'tag': constants.PRODUCT_TAG
                    }
                )
            )
            kb.add(button)
            description = p.description if p.description else ''
            bot.send_photo(
                call.message.chat.id,
                p.image.read(),
                caption=f'{p.title}\n{description}',
                reply_markup=kb
            )


@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants.PRODUCT_TAG)
def handle_add_to_cart(call):
    product_id = json.loads(call.data)['id']
    product = Product.objects.get(id=product_id)
    user = User.objects.get(telegram_id=call.message.chat.id)
    cart = user.get_active_cart()
    cart.add_product(product)
    bot.answer_callback_query(
        call.id,
        'Продукт добавлен в корзину'
    )


# @bot.message_handler(content_types=['text'])
# def handler_test(message):
#     print('handler text')