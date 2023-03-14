
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def course_list():
    return {"Hello": "World"}

@app.get("/{course_id}")
def course_detail(course_id: int):
    return {"Hello": "World"}