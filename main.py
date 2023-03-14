from fastapi import FastAPI, File, UploadFile, Form

from routes import auth, chat, course

app = FastAPI()

app.mount

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/chat/completion")
async def chat_completion(file: UploadFile = File(), course: int = Form()):
    return {"Hello": "World"}
