import datetime

from . import me
# import mongoengine as me
# me.connect('SHOP')


#class CreationTime(me.Document):
class CreationTime(me.EmbeddedDocument):
    created_time = me.DateTimeField()
    modified_time = me.DateTimeField()

    # def save(self, *args, **kwargs):
    #     if self.created_time:
    #         self.modified_time = datetime.datetime.now()
    #     else:
    #         self.created_time = datetime.datetime.now()
    #
    #     super().save(*args, **kwargs)


class News(me.Document):
    title = me.StringField(required=True, min_length=2, max_length=256)
    body = me.StringField(required=True, min_length=2, max_length=2048)
    # TODO use abstract datetime class
    # creation_time = me.ReferenceField(CreationTime)
    creation_time = me.EmbeddedDocumentField(CreationTime)

    def save(self, *args, **kwargs):
        if self.creation_time:
            self.creation_time.modified_time = datetime.datetime.now()
        else:
            self.creation_time = CreationTime()
            self.creation_time.created_time = datetime.datetime.now()

        super().save(*args, **kwargs)
