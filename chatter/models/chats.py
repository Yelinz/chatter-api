from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator


class Chats(Model):
    id = fields.UUIDField(pk=True)
    rating = fields.IntField(null=True)
    course = fields.ForeignKeyField("models.Courses", related_name="chats")
    user = fields.ForeignKeyField("models.Users", related_name="chats")


Chat_Pydantic = pydantic_model_creator(Chats, name="Chat")
