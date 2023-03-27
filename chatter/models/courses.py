from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model

from chatter.models.chats import Chats


class Courses(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=128)
    description = fields.CharField(max_length=4096)
    """
    prompt and inital_message should just be message relations
    """
    prompt = fields.CharField(max_length=4096)
    inital_message = fields.CharField(max_length=4096)

    chats: fields.ReverseRelation["Chats"]


Course_Pydantic = pydantic_model_creator(Courses, name="Course")
