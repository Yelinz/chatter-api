from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model

from chatter.models.messages import Messages


class Chats(Model):
    id = fields.UUIDField(pk=True)
    rating: int | None = fields.IntField(null=True)
    course = fields.ForeignKeyField("models.Courses", related_name="chats")
    user = fields.ForeignKeyField("models.Users", related_name="chats")
    created_at = fields.DatetimeField(auto_now_add=True)

    messages: fields.ReverseRelation["Messages"]

    def serialized_messages(self) -> list[dict]:
        return list(
            map(
                lambda message: message.dict(),
                [self.course.inital_message, *self.messages.all()],
            )
        )

    class PydanticMeta:
        computed = ("serialized_messages",)


Chat_Pydantic = pydantic_model_creator(Chats, name="Chat")
