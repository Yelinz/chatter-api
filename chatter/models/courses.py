from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator


class Courses(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=128)
    description = fields.CharField(max_length=4096)
    prompt = fields.CharField(max_length=4096)
    inital_message = fields.CharField(max_length=4096)


Course_Pydantic = pydantic_model_creator(Courses, name="Course")
