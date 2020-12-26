import json

from flask_restful import Resource, Api, request
from flask import Flask

from ..models.shop_models import Category, Product


class CategoryResources(Resource):
    def get(self, cat_id=None):
        print(cat_id)
        if cat_id:
            cat = Category.objects.get(cat_id)
            return json.loads(cat.to_json())
        else:
            cat = Category.objects()
            return json.loads(cat.to_json())

    def post(self):
        title = request.json.get('title')
        desc = request.json.get('description')
        parent = request.json.get('parent')
        # subcategories = request.json.get('subcategories')
        print(f'title:{title}, desc:{desc}, parent:{parent}')

        cat = Category.objects(title=title)
        if cat:
            return {'Error:': f'Category {title} exists'}

        if parent:
            print('add subcategory in category')
            root_cat = Category.objects(title=parent).first()
            if root_cat:
                print('cat ex')
                new_cat = Category(title=title, description=desc).save()
                root_cat.add_subcategory(new_cat)
                return {'Success': f'Category {title} added in parent {parent}'}
            else:
                return {'Error': f'Parent category {parent} doesnt exists'}

        else:
            Category(title=title, description=desc).save()
            return {'Success': f'Category {title} added as root category'}

    def delete(self, cat_id):
        cat = Category.objects(id=cat_id).first()
        if cat:
            print(cat.id)
            sub_cat = Category.objects(subcategories=cat).first()

            print(sub_cat.subcategories)
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


        # title = request.json.get('title')
        # discount = request.json.get('discount')
        # price = request.json.get('price')
        # category = request.json.get('category')
        # in_stock = request.json.get('in_stock')
        print(
            f'title:{title}; discount:{discount}; price:{price} '
            f'category:{category}; in_stock:{in_stock}'
        )

        # get category id
        cat = Category.objects(title=category).first()
        print(cat)

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
