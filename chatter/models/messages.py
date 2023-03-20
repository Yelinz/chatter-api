from enum import Enum

from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class Messages(Model):
    id = fields.UUIDField(pk=True)
    content = fields.CharField(max_length=4096)
    role = fields.CharEnumField(Role)
    chat = fields.ForeignKeyField("models.Chats", related_name="messages", null=True)

    @property
    def serialized(self):
        return {
            "content": self.content,
            "role": self.role,
        }


Message_Pydantic = pydantic_model_creator(Messages, name="Message")
