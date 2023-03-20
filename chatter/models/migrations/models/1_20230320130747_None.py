from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "courses" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(128) NOT NULL,
    "description" VARCHAR(4096) NOT NULL,
    "prompt" VARCHAR(4096) NOT NULL,
    "inital_message" VARCHAR(4096) NOT NULL
);
CREATE TABLE IF NOT EXISTS "users" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(64) NOT NULL,
    "email" VARCHAR(64) NOT NULL
);
CREATE TABLE IF NOT EXISTS "chats" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "rating" INT NOT NULL,
    "course_id" UUID NOT NULL REFERENCES "courses" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "messages" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "content" VARCHAR(4096) NOT NULL,
    "role" VARCHAR(9) NOT NULL,
    "chat_id" UUID REFERENCES "chats" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "messages"."role" IS 'system: system\nuser: user\nassistant: assistant';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
