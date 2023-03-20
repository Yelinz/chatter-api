from uuid import UUID

from fastapi import APIRouter

from chatter.models.users import User_Pydantic, Users

router = APIRouter()


@router.get("/{user_id}", response_model=User_Pydantic)
async def user_detail(user_id: UUID):
    return await User_Pydantic.from_queryset_single(Users.get(id=user_id))
