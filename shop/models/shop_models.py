from . import me


class User(me.Document):
    telegram_id = me.IntField(primary_key=True)
    username = me.StringField(min_length=2, max_length=128)
    prone_number = me.StringField(max_length=12)
    email = me.EmailField()
    is_block = me.BooleanField(default=False)


class Category(me.Document):
    title = me.StringField(required=True)
    description = me.StringField(min_length=512)
    parent = me.ReferenceField('self')
    subcategories = me.ListField(me.ReferenceField('self'))

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


class Product(me.Document):
    title = me.StringField(required=True, max_length=256)
    description = me.StringField(min_length=512)
    in_stock = me.BooleanField(defautl=True)
    discount = me.IntField(min_value=0, max_value=100, default=0)
    price = me.FileField(required=True)
    image = me.FileField()
    category = me.ReferenceField(Category, required=True)
