from . import me

import datetime


class User(me.Document):
    telegram_id = me.IntField(primary_key=True)
    username = me.StringField(min_length=2, max_length=128)
    first_name = me.StringField(min_length=2, max_length=128)
    phone_number = me.StringField(max_length=12)
    email = me.EmailField()
    home_address = me.StringField(max_length=20)
    is_block = me.BooleanField(default=False)

    def get_active_cart(self):
        cart = Cart.objects(user=self, is_active=True).first()

        if cart is None:
            # cart = Cart.objects.create(
            #     user=self
            # )
            cart = Cart(user=self)
            cart.save()
        return cart

    def formated_data(self):
        return f'ID - {self.telegram_id}\nNickname - {self.username}\nName - {self.first_name}\n' \
               f'Email - {self.email}\nPhone number - {self.phone_number}\nAddress - {self.home_address}'


class Category(me.Document):
    title = me.StringField(required=True)
    description = me.StringField(min_length=100)
    parent = me.ReferenceField('self')
    subcategories = me.ListField(me.ReferenceField('self'))

    def get_products(self):
        return Product.objects(category=self)

    @classmethod
    def get_root_categories(cls):
        return cls.objects(
            parent=None
        )

    def is_root(self):
        return not bool(self.parent)

    def add_subcategory(self, category):
        category.parent = self
        category.save()

        self.subcategories.append(category)
        self.save()


class Parameters(me.EmbeddedDocument):
    height = me.FloatField()
    width = me.FloatField()
    weight = me.FloatField()
    additional_description = me.StringField()


class Product(me.Document):
    title = me.StringField(required=True, max_length=256)
    description = me.StringField(min_length=10)
    in_stock = me.BooleanField(defautl=True)
    discount = me.IntField(min_value=0, max_value=100, default=0)
    price = me.IntField(required=True)
    image = me.FileField()
    category = me.ReferenceField(Category, required=True)
    parameters = me.EmbeddedDocumentField(Parameters)

    @property
    def product_price(self):
        return (100 - self.discount) / 100 * self.price


class Cart(me.Document):
    user = me.ReferenceField(User, required=True)
    products = me.ListField(me.ReferenceField(Product))
    is_active = me.BooleanField(default=True)
    created_at = me.DateTimeField()

    def save(self, *args, **kwargs):
        self.created_at = datetime.datetime.now()
        super().save(*args, **kwargs)

    def add_product(self, product):
        self.products.append(
            product
        )
        self.save()

    def delete_product(self, product):
        product_list = []

        # Находим индексы продуктов, которые нужно удалить в списке продуктов
        for i, p in enumerate(self.products.copy()):
            if p == product:
                product_list.append(i)

        # Удаляем продукты начиная с последнего индекса
        i = len(product_list) - 1
        while True:
            if i < 0:
                break
            self.products.pop(product_list[i])
            i -= 1

        self.save()

    def increase_product(self, product):
        self.add_product(product)

    def decrease_product(self, product):
        product_list = []
        for i, p in enumerate(self.products.copy()):
            if p == product:
                product_list.append(i)

        if product_list:
            self.products.pop(product_list[(len(product_list) - 1)])
            self.save()

    def cart_checkout(self):
        self.is_active = False
        self.save()
