from fastapi import FastAPI, File, UploadFile, Form

app = FastAPI()


@app.get("/{chat_id}}")
def chat_detail():
    return {"Hello": "World"}

@app.post("/{chat_id}/new-message")
async def chat_completion(file: UploadFile = File()):
    """
    1. speech to text: whisper
    2. text moderation: openai endpoint
    3. text to completion: chatgpt
    4. completion to tts, translation, suggestion: ms voice, deepl, chatgpt

    return completion, tts and suggestion
    """
    return {"Hello": "World"}

@app.get("/{chat_id}/{message_id}")
def chat_message_detail():
    return {"Hello": "World"}

