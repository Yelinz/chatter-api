
from core.config import settings

def test_new_message(
    client: TestClient, chat: Chat_Pydantic
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/chats/{chat.id}/new-message",
        json=data,
    )

    assert r.status_code == 200