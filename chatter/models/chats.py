from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class Chats(Model):
    id = fields.UUIDField(pk=True)
    rating = fields.IntField(null=True)
    course = fields.ForeignKeyField("models.Courses", related_name="chats")
    user = fields.ForeignKeyField("models.Users", related_name="chats")

    @property
    def serialized_messages(self):
        return [message.serialized for message in self.messages]


Chat_Pydantic = pydantic_model_creator(Chats, name="Chat")
