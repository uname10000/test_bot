import json
import time

from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from mongoengine import NotUniqueError

from flask import Flask, request, abort
from flask_restful import Api

from ..models.shop_models import Category, User, Product
from ..models.extra_models import News
from .config import TOKEN, WEBHOOK_URL, WEBHOOK_URI
from .utils import inline_kb_from_iterable
from . import constants
from ..api.resurses import CategoryResources, ProductResource, NewsResource, CartResource

# botname: Shptestbot
# bot username: Shptest_bot
bot = TeleBot(TOKEN)

app = Flask(__name__)
api = Api(app)
api.add_resource(CategoryResources, '/category', '/category/<string:cat_id>')
api.add_resource(ProductResource, '/product', '/product/<string:prod_id>')
api.add_resource(NewsResource, '/news', '/news/<string:news_id>')
api.add_resource(CartResource, '/cart', '/cart/<string:cart_id>')


@app.route(WEBHOOK_URI, methods=['POST'])
def handle_webhook():
    print(request.get_data())
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''

    abort(403)


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
    user = User.objects.get(telegram_id=message.chat.id)
    cart = user.get_active_cart()

    products_grouped_by_id = dict()
    for p in cart.products:
        if p.id in products_grouped_by_id.keys():
            products_grouped_by_id[p.id]['title'] = p.title
            products_grouped_by_id[p.id]['count'] += 1
        else:
            products_grouped_by_id[p.id] = {
                'title': p.title,
                'count': 1,
                'price': p.product_price,
                'image': p.image
            }

    for k, v in products_grouped_by_id.items():
        kb = InlineKeyboardMarkup()
        delete_button = InlineKeyboardButton(
            text=f'Удалить "{v["title"]}"',
            callback_data=json.dumps(
                {
                    'id': str(k),
                    'tag': constants.PRODUCT_DELETE_TAG
                }
            )
        )

        increase_count_button = InlineKeyboardButton(
            text='Увеличить количество',
            callback_data=json.dumps(
                {
                    'id': str(k),
                    'tag': constants.PRODUCT_INCREASE_COUNT
                }
            )
        )

        decrease_count_button = InlineKeyboardButton(
            text='Уменьшить количество',
            callback_data=json.dumps(
                {
                    'id': str(k),
                    'tag': constants.PRODUCT_DECREASE_COUNT
                }
            )
        )

        kb.add(increase_count_button, decrease_count_button)
        kb.add(delete_button)

        # bot.send_message(
        #     message.chat.id,
        #     f'{v["title"]} | Цена: {v["price"]}',
        #     reply_markup=kb
        # )
        bot.send_photo(
            message.chat.id,
            v['image'].read(),
            caption=f'{v["title"]}\nЦена: {v["price"]}\nКоличество: {v["count"]}',
            reply_markup=kb
        )

    total_price = 0

    for k, v in products_grouped_by_id.items():
        total_price += v['price']

    kb = InlineKeyboardMarkup(row_width=1)
    checkout_button = InlineKeyboardButton(
        text='Оформить заказ',
        callback_data=json.dumps(
            {
                'id': 'id cart',
                'tag': constants.CART_CHECKOUT
            }
        )
    )

    # Если нет товаров - кнопка "Оформить заказ" не нужна
    if products_grouped_by_id:
        kb.add(checkout_button)

    bot.send_message(
        message.chat.id,
        f'Стоимость заказа: {total_price}\nЖелаете оформить заказ?',
        reply_markup=kb
    )


@bot.message_handler(func=lambda m: constants.START_KB[constants.NEWS] == m.text)
def handler_message_news(message):
    news = News.objects()
    sorted_news = []

    for n in news:
        sorted_news.append(n)

    if news:
        for i in range(len(sorted_news)):
            for j in range(len(sorted_news) - 1):
                if sorted_news[j].creation_time.created_time.replace(microsecond=0) < sorted_news[j + 1].creation_time.created_time.replace(microsecond=0):
                    buf = sorted_news[j]
                    sorted_news[j] = sorted_news[j + 1]
                    sorted_news[j + 1] = buf

        rng = 0
        if len(sorted_news) < 5:
            rng = len(sorted_news)
        else:
            rng = 5

        for i in range(rng):
            bot.send_message(
                message.chat.id,
                f'{sorted_news[i].title}\n{sorted_news[i].body}'
            )


@bot.message_handler(func=lambda m: constants.START_KB[constants.PRODUCTS_WITH_DISCOUNTS] == m.text)
def handler_message_prod_with_disc(message):
    products = Product.objects(discount__ne=0)

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
        price = p.product_price

        bot.send_photo(
            message.chat.id,
            p.image.read(),
            caption=f'{p.title}\n{description}\nЦена:{price}',
            reply_markup=kb
        )


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
            price = p.product_price

            bot.send_photo(
                call.message.chat.id,
                p.image.read(),
                caption=f'{p.title}\n{description}\nЦена:{price}',
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
        f'Продукт "{product.title}" добавлен в корзину'
    )


@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants.PRODUCT_DELETE_TAG)
def handle_delete_product_from_cart(call):
    product_id = json.loads(call.data)['id']
    product = Product.objects.get(id=product_id)
    user = User.objects.get(telegram_id=call.message.chat.id)
    cart = user.get_active_cart()
    cart.delete_product(product)
    bot.answer_callback_query(
        call.id,
        f'Продукт "{product.title}" удален из корзины'
    )



@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants.PRODUCT_INCREASE_COUNT)
def handle_product_increase_count(call):
    product_id = json.loads(call.data)['id']
    product = Product.objects.get(id=product_id)
    user = User.objects.get(telegram_id=call.message.chat.id)
    cart = user.get_active_cart()
    cart.increase_product(product)
    bot.answer_callback_query(
        call.id,
        f'Продукт "{product.title}" количество увеличено на 1'
    )


@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants.PRODUCT_DECREASE_COUNT)
def handle_product_decrease_count(call):
    product_id = json.loads(call.data)['id']
    product = Product.objects.get(id=product_id)
    user = User.objects.get(telegram_id=call.message.chat.id)
    cart = user.get_active_cart()
    cart.decrease_product(product)
    bot.answer_callback_query(
        call.id,
        f'Продукт "{product.title}" количество уменьшено на 1'
    )


@bot.callback_query_handler(lambda c: json.loads(c.data)['tag'] == constants.CART_CHECKOUT)
def handle_cart_checkout(call):
    # product_id = json.loads(call.data)['id']
    # product = Product.objects.get(id=product_id)
    user = User.objects.get(telegram_id=call.message.chat.id)
    cart = user.get_active_cart()
    cart.cart_checkout()
    bot.answer_callback_query(
        call.id,
        f'Спасибо за покупку товаров!'
    )



