import asyncio
import subprocess
from uuid import UUID

import aiohttp
import numpy as np
import whisper
from fastapi import APIRouter, File, Form, UploadFile

from chatter.core.config import settings
from chatter.core.http_clients import Clients
from chatter.models.chats import Chat_Pydantic, Chats
from chatter.models.courses import Course_Pydantic
from chatter.models.messages import Message_Pydantic, Messages
from chatter.schemas.completion import Completion_Response

router = APIRouter()

model = whisper.load_model("tiny")  # TODO: use large later


@router.post("/", status_code=201)
async def chat_create(course_id: UUID) -> Chat_Pydantic:
    chat_obj = await Chats.create(
        course_id=course_id, user_id=UUID("891b80aa-61ec-4ee0-b6bd-4e142632a8ab")
    )
    return chat_obj


@router.get("/{chat_id}")
async def chat_detail(chat_id: UUID) -> Chat_Pydantic:
    return await Chat_Pydantic.from_queryset_single(Chats.get(id=chat_id))


async def audio_to_text(file: UploadFile) -> str:
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
    audio_out, errordata = process.communicate(await file.read())
    ndarr = np.frombuffer(audio_out, np.int16).flatten().astype(np.float32) / 32768.0

    # enable fp16 for faster inference when using a GPU
    # set language from user or http
    result = model.transcribe(audio=ndarr, language="en", fp16=False)

    return result["text"]


async def text_to_audio(text: str) -> bytes:
    async with Clients.azure.post(
        "/cognitiveservices/v1",
        body=f"""
                '<speak version='\''1.0'\'' xml:lang='\''en-US'\''>
                    <voice xml:lang='\''en-US'\'' xml:gender='\''Female'\'' name='\''en-US-JennyNeural'\''>
                    {text}
                    </voice>
                </speak>'
            """,
    ) as response:
        return await response.read()


@router.post("/{chat_id}/new-message")
async def chat_completion(chat_id: UUID, file: UploadFile) -> Completion_Response:
    """
    1. speech to text: whisper
    2. text moderation: openai endpoint
    3. text to completion: chatgpt, maybe own alpaca model
    4. completion to tts, translation, suggestion: ms voice, deepl, chatgpt

    return completion, tts and suggestion
    """

    transcript: str = await audio_to_text(file)

    if settings.ENABLE_MODERATION:
        async with Clients.openai.post(
            "/v1/moderations", json={"input": transcript}
        ) as response:
            moderation_response = await response.json()

            if moderation_response["results"][0]["flagged"]:
                return "TODO: moderation error"

    chat = await Chats.get(id=chat_id)
    # await Messages.create(chat=chat, content=transcript, role="user"),
    messages = await Message_Pydantic.from_queryset(chat.messages.all())
    serialized_messages = list(
        map(
            lambda message: {"content": message.content, "role": message.role}, messages
        )
    )

    async with Clients.openai.post(
        "/v1/chat/completions",
        json={
            "model": "gpt-3.5-turbo",
            "messages": serialized_messages,
            "max_tokens": 2000,
            "temperature": 1,
            "top_p": 1,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.5,
            "user": "TODO",
        },
    ) as response:
        completion_response = await response.json()

    print(completion_response)
    if "error" in completion_response:
        # TODO: handle error
        return completion_response["error"]

    completion_text = completion_response["choices"][0]["message"]["content"]

    translation = completion_text
    suggestions = [{"text": completion_text, "translation": completion_text}]

    results = await asyncio.gather(
        Messages.create(chat=chat, content=completion_text, role="assistant"),
        text_to_audio(completion_text),
    )

    return {
        "user_text": transcript,
        "assistant_text": completion_text,
        "assistant_translation": translation,
        "assistant_audio": results[1],
        "suggestions": suggestions,
    }


@router.post("/{chat_id}/rating")
async def chat_message_detail(chat_id: UUID, rating: int) -> Chat_Pydantic:
    chat = await Chat_Pydantic.from_queryset_single(Chats.get(id=chat_id))
    chat.rating = rating
    await chat.save()
    return chat
