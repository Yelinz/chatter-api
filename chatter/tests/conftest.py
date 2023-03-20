from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.config import settings
from db.session import SessionLocal
from main import app
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def chat() -> Chat_Pydantic:
    return Chat_Pydantic(
        id=UUID("891b80aa-61ec-4ee0-b6bd-4e142632a8ab"),
        course_id=UUID("891b80aa-61ec-4ee0-b6bd-4e142632a8ab"),
        user_id=UUID("891b80aa-61ec-4ee0-b6bd-4e142632a8ab"),
    )
