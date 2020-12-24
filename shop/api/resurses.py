import json

from flask_restful import Resource, Api, request
from flask import Flask

from ..models.shop_models import Category


class CategoryResources(Resource):
    def get(self, id_=None):
        print(id_)
        if id_:
            cat = Category.objects.get(id=id_)
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
