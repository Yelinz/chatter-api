from chatter.models.courses import Course_Pydantic, Courses
from fastapi import APIRouter
from uuid import UUID

router = APIRouter()


@router.get("/", response_model=list[Course_Pydantic])
async def course_list():
    return await Course_Pydantic.from_queryset(Courses.all())


@router.get("/{course_id}", response_model=Course_Pydantic)
async def course_detail(course_id: UUID):
    return await Course_Pydantic.from_queryset_single(Courses.get(id=course_id))
