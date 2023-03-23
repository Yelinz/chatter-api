from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model

from chatter.models.courses import Courses
from chatter.models.messages import Messages


class Users(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=64)
    email = fields.CharField(max_length=64)

    chats: fields.ReverseRelation["Courses"]
    messages: fields.ReverseRelation["Messages"]


User_Pydantic = pydantic_model_creator(Users, name="User")
