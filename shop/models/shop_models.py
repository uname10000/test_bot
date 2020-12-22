from . import me

import datetime


class User(me.Document):
    telegram_id = me.IntField(primary_key=True)
    username = me.StringField(min_length=2, max_length=128)
    first_name = me.StringField(min_length=2, max_length=128)
    prone_number = me.StringField(max_length=12)
    email = me.EmailField()
    is_block = me.BooleanField(default=False)

    def get_active_cart(self):
        cart = Cart.objects(user=self, is_active=True).first()

        if not cart:
            cart = Cart.objects.create(
                user=self
            )

        return cart

    def formated_data(self):
        return f'id - {self.telegram_id}\nnickname - {self.username}\nname - {self.first_name}\nEmail - {self.email}\nPhone number - {self.prone_number}'


class Category(me.Document):
    title = me.StringField(required=True)
    description = me.StringField(min_length=512)
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
    description = me.StringField(min_length=512)
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
