from fastapi import APIRouter

from chatter.api.api_v1.endpoints import login, users, chat, course, message

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(course.router, prefix="/course", tags=["course"])
api_router.include_router(message.router, prefix="/message", tags=["message"])
