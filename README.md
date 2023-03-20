# Chatter API

FastAPI, Tortoise ORM

# Requirements
Python 3.10
docker compose

## Configuration
All configuration is done via .env file

OPENAI_API_KEY - OpenAI API key

## Start the server
```sh
docker compose build
docker compose up -d
```

If the docker service is not running, you can start it with the following command:
sudo service docker start

# Development
Create and execute migrations
```sh
docker compose exec api aerich migrate
docker compose exec api aerich upgrade
```
