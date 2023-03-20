from chatter.models.messages import Message_Pydantic, Messages
from fastapi import APIRouter
from uuid import UUID

router = APIRouter()


@router.get("/", response_model=list[Message_Pydantic])
async def message_list(chat_id: UUID):
    return await Message_Pydantic.from_queryset(Messages.get(chat_id=chat_id))


@router.get("/{message_id}", response_model=Message_Pydantic)
async def message_detail(message_id: UUID):
    return await Message_Pydantic.from_queryset_single(Messages.get(id=message_id))
