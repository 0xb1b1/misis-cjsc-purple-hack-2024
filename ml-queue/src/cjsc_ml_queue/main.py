#!/usr/bin/env python3
import uvicorn
import redis
import sys
from fastapi import FastAPI
from cjsc_ml_queue.models import Message, MessageRequestConfig, MessageRequest

app = FastAPI()

# Connect to the Redis server
redis_conn = redis.Redis(
    host='localhost',
    port=6379,
    db=0
)


# Function to push an item to the queue
def push_to_queue(redis_conn, item):
    redis_conn.lpush('requests', item)


@app.post("/query_ml")
async def query_ml(mr: MessageRequest):
    # Push the request to the queue
    push_to_queue(redis_conn, mr.json())
    return {"status": "ok"}


@app.post("/ml_answer")
async def ml_answer(m: Message):
    ...  # Send POST to backend with the message


def run():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8081,
    )


if __name__ == "__main__":
    run()
    sys.exit(0)