import requests
from chatter.core.config import settings
from chatter.models.chats import Chat_Pydantic, Chats
from chatter.models.courses import Course_Pydantic
from chatter.models.messages import Messages
from fastapi import APIRouter, File, UploadFile, Form
import asyncio
import whisper
import torchaudio

router = APIRouter()

model = whisper.load_model("tiny")  # TODO: probably use large later

OPENAI_HEADERS = {
    "Authorization": "Bearer " + settings.OPENAI_API_KEY,
    "Content-Type": "application/json",
}
AZURE_HEADERS = {
    "Ocp-Apim-Subscription-Key": settings.AZURE_API_KEY,
    "Content-Type": "application/ssml+xml",
    "X-Microsoft-OutputForma": "audio-16khz-128kbitrate-mono-mp3",
}


@router.post("/", response_model=Chat_Pydantic)
async def chat_create(course: Course_Pydantic):
    # TODO: add user relation
    chat_obj = await Chats.create(**course.dict(exclude_unset=True))
    return await Chat_Pydantic.from_tortoise_orm(chat_obj)


@router.get("/{chat_id}}", response_model=Chat_Pydantic)
async def chat_detail(chat_id: int):
    return await Chat_Pydantic.from_queryset_single(Chats.get(id=chat_id))


@router.post("/{chat_id}/new-message")
async def chat_completion(chat_id: int, file: UploadFile = File()):
    """
    1. speech to text: whisper
    2. text moderation: openai endpoint
    3. text to completion: chatgpt
    4. completion to tts, translation, suggestion: ms voice, deepl, chatgpt

    return completion, tts and suggestion
    """

    # TODO: file to ndarray or tensor
    tensor = torchaudio.load(await file.read())
    result = await model.transcribe(tensor)
    transcript = result["text"]

    moderation_response = await requests.post(
        "https://api.openai.com/v1/moderations",
        headers=OPENAI_HEADERS,
        json={"input": transcript},
    )

    if moderation_response["result"]["flagged"]:
        return "BAD REQUEST"

    chat = await Chat_Pydantic.from_queryset_single(Chats.get(id=chat_id))
    messages = chat.messages  # TODO: serialize
    completion_response = await requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=OPENAI_HEADERS,
        json={
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 1,
            "top_p": 1,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.5,
            "user": "TODO",
        },
    )

    completion_text = completion_response["choices"][0]["text"]

    results = await asyncio.gather(
        Messages.create(chat=chat, text=transcript, role="user"),
        Messages.create(chat=chat, text=completion_text, role="assistant"),
        requests.post(
            "switzerlandnorth.tts.speech.microsoft.com/cognitiveservices/v1",
            body="""
                '<speak version='\''1.0'\'' xml:lang='\''en-US'\''>
                    <voice xml:lang='\''en-US'\'' xml:gender='\''Female'\'' name='\''en-US-JennyNeural'\''>
                    {completion_text}
                    </voice>
                </speak>'
            """,
        ),
    )

    return chat.messages


@router.get("/{chat_id}/rating")
async def chat_message_detail(chat_id: int, rating: int):
    chat = await Chat_Pydantic.from_queryset_single(Chats.get(id=chat_id))
    chat.rating = rating
    await chat.save()
    return chat
