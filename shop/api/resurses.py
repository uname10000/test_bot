import json

from flask_restful import Resource, Api, request
from flask import Flask

from ..models.shop_models import Category, Product, Cart, User, Parameters
from ..models.extra_models import News


class CategoryResources(Resource):
    def get(self, cat_id=None):
        if cat_id:
            cat = Category.objects.get(id=cat_id)
            return json.loads(cat.to_json())
        else:
            cat = Category.objects()
            return json.loads(cat.to_json())

    def post(self):
        title = request.json.get('title')
        desc = request.json.get('description')
        parent = request.json.get('parent')
        # subcategories = request.json.get('subcategories')

        cat = Category.objects(title=title)
        if cat:
            return {'Error:': f'Category {title} exists'}

        if parent:
            root_cat = Category.objects(title=parent).first()
            if root_cat:
                new_cat = Category(title=title, description=desc).save()
                root_cat.add_subcategory(new_cat)
                return {'Success': f'Category {title} added in parent {parent}'}
            else:
                return {'Error': f'Parent category {parent} doesnt exists'}

        else:
            Category(title=title, description=desc).save()
            return {'Success': f'Category {title} added as root category'}

    def put(self, cat_id):
        cat = Category.objects(id=cat_id)
        if cat:
            title = request.json.get('title')
            description = request.json.get('description')
            parent = request.json.get('parent')

            if title:
                cat.update(set__title=title)
            if description:
                cat.update(set__description=description)
            if parent:
                root_cat = Category.objects(title=parent).first()
                if root_cat:
                    new_cat = Category(title=title, description=description).save()
                    root_cat.add_subcategory(new_cat)
                else:
                    return {'Error': f'Parent category {parent} doesnt exists'}
            # cat.save()
            return {'Success': f'Category {cat_id} updated'}
        else:
            return {'Error:': f'Category {cat_id} doesnt exists'}

    def delete(self, cat_id):
        cat = Category.objects(id=cat_id).first()
        if cat:
            # print(cat.id)
            sub_cat = Category.objects(subcategories=cat).first()

            # print(sub_cat.subcategories)
            new_sub_cat = []
            for sub in sub_cat.subcategories:
                if sub.id != cat.id:
                    new_sub_cat.append(sub)

            sub_cat.update(subcategories=new_sub_cat)
            cat.delete()
            return {'Success': f'Category {cat_id} was deleted'}
        else:
            return {'Error': f'Category {cat_id} not found'}


class ProductResource(Resource):
    def get(self, prod_id=None):
        if prod_id:
            product = Product.objects.get(id=prod_id)
            return json.loads(product.to_json())
        else:
            product = Product.objects()
            return json.loads(product.to_json())

    def post(self):
        title = request.form.get('title')
        discount = request.form.get('discount')
        price = request.form.get('price')
        category = request.form.get('category')
        in_stock = request.form.get('in_stock')
        description = request.form.get('description')
        file = request.files['image']
        tmp_filename = file.filename
        file.save(tmp_filename)
        file.close()

        param_weight = request.form.get('weight')
        param_height = request.form.get('height')
        param_width = request.form.get('width')
        param_additional_description = request.form.get('additional_description')


        # title = request.json.get('title')
        # discount = request.json.get('discount')
        # price = request.json.get('price')
        # category = request.json.get('category')
        # in_stock = request.json.get('in_stock')
        # print(
        #     f'title:{title}; discount:{discount}; price:{price} '
        #     f'category:{category}; in_stock:{in_stock}'
        # )

        # get category id
        cat = Category.objects(title=category).first()

        if cat:
            product = Product.objects(title=title).first()
            if product:
                return {'Error': f'Product {product.title} already exist'}
            else:
                if not description:
                    description = ''
                b_file = open(tmp_filename, 'rb')
                product = Product(
                    title=title, discount=discount, price=price, category=cat.id, in_stock=in_stock,
                    description=description
                )
                product.image.put(b_file, content_type='image/jpeg')

                product.parameters = Parameters()
                if param_weight:
                    product.parameters.weight = float(param_weight)
                if param_height:
                    product.parameters.height = float(param_height)
                if param_width:
                    product.parameters.width = float(param_width)
                if param_additional_description:
                    product.parameters.additional_description = str(param_additional_description)
                product.save()
                b_file.close()
                return {'Success': f'Product {title} added in category {cat.title}'}
        else:
            return {'Error': f'Category {category} doesnt exist'}

    def delete(self, prod_id):
        product = Product.objects(id=prod_id).first()

        if product:
            product.delete()
            return {'Success': f'Product with id {prod_id} was deleted'}
        else:
            return {'Error': f'Product with id: {prod_id} doesnt exists'}

    def put(self, prod_id):
        if prod_id:
            product = Product.objects(id=prod_id).first()
            title = request.form.get('title')
            discount = request.form.get('discount')
            price = request.form.get('price')
            category = request.form.get('category')
            in_stock = request.form.get('in_stock')
            description = request.form.get('description')
            try:
                file = request.files['image']
                tmp_filename = file.filename
                file.save(tmp_filename)
                file.close()
            except:
                file = None

            param_weight = request.form.get('weight')
            param_height = request.form.get('height')
            param_width = request.form.get('width')
            param_additional_description = request.form.get('additional_description')

            if title:
                product.update(set__title=title)
            if discount:
                product.update(set__discount=discount)
            if price:
                product.update(set__price=price)

            if category:
                cat = Category.objects(title=category).first()
                if cat:
                    product.update(set__category=cat.id)
                else:
                    return {'Error': f'Category {category} doesnt exist'}
            if in_stock:
                product.update(set__in_stock=in_stock)
            if description:
                product.update(set__description=description)
            if file:
                product.image.delete()
                b_file = open(tmp_filename, 'rb')
                product.image.put(b_file, content_type='image/jpeg')
                b_file.close()
            if param_weight:
                if product.parameters:
                    product.parameters.weight = float(param_weight)
                else:
                    product.parameters = Parameters()
                    product.parameters.weight = float(param_weight)
            if param_height:
                if product.parameters:
                    product.parameters.height = float(param_height)
                else:
                    product.parameters = Parameters()
                    product.parameters.height = float(param_height)
            if param_width:
                if product.parameters:
                    product.parameters.width = float(param_width)
                else:
                    product.parameters = Parameters()
                    product.parameters.width = float(param_width)
            if param_additional_description:
                if product.parameters:
                    product.parameters.additional_description = str(param_additional_description)
                else:
                    product.parameters = Parameters()
                    product.parameters.additional_description = str(param_additional_description)

            product.save()

            return {'Success': f'Product with id: {prod_id} was updated'}

        else:
            return {'Error': f'Product with id: {prod_id} doesnt exists'}


class NewsResource(Resource):
    def get(self, news_id=None):
        if news_id:
            news = News.objects.get(id=news_id)
            return json.loads(news.to_json())
        else:
            news = News.objects()
            return json.loads(news.to_json())

    def post(self):
        title = request.json.get('title')
        body = request.json.get('body')

        news = News.objects(title=title)
        if news:
            return {'Error': f'News with title: {title} exists'}
        else:
            news = News(title=title, body=body)
            news.save()
            return {'Success': f'News with title: {title} was created'}

    def delete(self, news_id):
        news = Product.objects(id=news_id).first()

        if news:
            news.delete()
            return {'Success': f'News with id {news_id} was deleted'}
        else:
            return {'Error': f'News with id: {news_id} doesnt exists'}


class CartResource(Resource):
    def get(self, cart_id=None):
        if cart_id:
            cart = Cart.objects(id=cart_id)
            return json.loads(cart.to_json())
        else:
            cart = Cart.objects()
            return json.loads(cart.to_json())

    def delete(self, cart_id):
        cart = Cart.objects(id=cart_id)
        if cart:
            cart.delete()
            return {'Success': f'Cart with id {cart_id} was deleted'}
        else:
            return {'Error': f'Cart with id {cart_id} doesnt exists'}


class UserResource(Resource):
    def get(self, user_id=None):
        if user_id:
            user = User.objects.get(telegram_id=user_id)
            return json.loads(user.to_json())
        else:
            user = User.objects()
            return json.loads(user.to_json())

    def put(self, user_id):
        user = User.objects.get(telegram_id=user_id)
        if user:
            first_name = request.json.get('first_name')
            username = request.json.get('username')
            phone_number = request.json.get('phone_number')
            home_address = request.json.get('home_address')
            email = request.json.get('email')
            
            if first_name:
                user.update(set__first_name=first_name)
            if username:
                user.update(set__username=username)
            if phone_number:
                user.update(set__phone_number=phone_number)
            if home_address:
                user.update(set__home_address=home_address)
            if email:
                user.update(set__email=email)

            user.save()
            return {'Success': f'User with id {user_id} was updated'}
        else:
            return {'Error': f'User with id {user_id} doesnt exists'}

    def delete(self, user_id):
        user = User.objects.get(telegram_id=user_id)
        if user:
            user.delete()
            return {'Success': f'User with id {user_id} was deleted'}
        else:
            return {'Error': f'User with id {user_id} doesnt exists'}
