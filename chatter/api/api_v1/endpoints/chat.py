import asyncio
import subprocess
from uuid import UUID

import numpy as np
import aiohttp
import whisper
from fastapi import APIRouter, File, Form, UploadFile

from chatter.core.config import settings
from chatter.models.chats import Chat_Pydantic, Chats
from chatter.models.courses import Course_Pydantic
from chatter.models.messages import Messages
from chatter.core.http_clients import Clients

router = APIRouter()

model = whisper.load_model("tiny")  # TODO: probably use large later


@router.post("/", response_model=Chat_Pydantic, status_code=201)
async def chat_create(course_id: UUID):
    chat_obj = await Chats.create(
        course_id=course_id, user_id=UUID("891b80aa-61ec-4ee0-b6bd-4e142632a8ab")
    )
    return chat_obj


@router.get("/{chat_id}", response_model=Chat_Pydantic)
async def chat_detail(chat_id: UUID):
    return await Chat_Pydantic.from_queryset_single(Chats.get(id=chat_id))


def audio_to_text(file: UploadFile) -> str:
    """
    recommended to use whisper.audio.load_audio() but it uses a file not a file-like object
    https://github.com/openai/whisper/blob/6dea21fd7f7253bfe450f1e2512a0fe47ee2d258/whisper/audio.py#L46
    """
    command = [
        "ffmpeg",
        "-y",
        "-i",
        "-",
        "-f",
        "s16le",
        "-acodec",
        "pcm_s16le",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-",
    ]
    process = subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    audio_out, errordata = process.communicate(file.read())
    ndarr = np.frombuffer(audio_out, np.int16).flatten().astype(np.float32) / 32768.0

    # enable fp16 for faster inference when using a GPU
    # set language from user setting
    result = model.transcribe(audio=ndarr, language="en", fp16=False)

    return result["text"]


@router.post("/{chat_id}/new-message")
async def chat_completion(chat_id: UUID, file: UploadFile):
    """
    1. speech to text: whisper
    2. text moderation: openai endpoint
    3. text to completion: chatgpt, maybe own alpaca model
    4. completion to tts, translation, suggestion: ms voice, deepl, chatgpt

    return completion, tts and suggestion
    """

    transcript = audio_to_text(file)

    async with Clients.openai.post(
        "/v1/moderations", json={"input": transcript}
    ) as response:
        moderation_response = await response.json()

        if moderation_response["result"]["flagged"]:
            return "TODO: moderation error"

    chat = await Chat_Pydantic.from_queryset_single(Chats.get(id=chat_id))
    messages = chat.serialized_messages

    async with Clients.openai.post(
        "/v1/chat/completions",
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
    ) as response:
        completion_response = await response.json()

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


@router.post("/{chat_id}/rating", response_model=Chat_Pydantic)
async def chat_message_detail(chat_id: UUID, rating: int):
    chat = await Chat_Pydantic.from_queryset_single(Chats.get(id=chat_id))
    chat.rating = rating
    await chat.save()
    return chat
