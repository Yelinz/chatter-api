import aiohttp
from fastapi import logger

OPENAI_HEADERS = {
    "Authorization": "Bearer " + settings.OPENAI_API_KEY,
    "Content-Type": "application/json",
}
AZURE_HEADERS = {
    "Ocp-Apim-Subscription-Key": settings.AZURE_API_KEY,
    "Content-Type": "application/ssml+xml",
    "X-Microsoft-OutputForma": "audio-16khz-128kbitrate-mono-mp3",
}

class Clients:
    openai: aiohttp.ClientSession | None = None

    @classmethod
    async def start_clients(self) -> None:
        logger.info("Starting aiohttp clients")
        self.openai_client = aiohttp.ClientSession(base_url="https://api.openai.com" ,headers=OPENAI_HEADERS)

    @classmethod
    async def close_clients(self) -> None:
        logger.info("Stopping aiohttp clients")
        await self.openai_client.close()