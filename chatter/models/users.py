from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class Users(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=64)
    email = fields.CharField(max_length=64)


User_Pydantic = pydantic_model_creator(Users, name="User")
