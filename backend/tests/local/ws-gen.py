#!/usr/bin/env python3
import asyncio
import sys

import socketio


async def run():
    # asyncio
    async with socketio.AsyncSimpleClient() as sio:
        await sio.connect("http://127.0.0.1:8080", namespace="/webapp")
        # Authenticate with JWT TOKEN
        await sio.emit(
            "auth",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWJqZWN0Ijp7ImlkIjowLCJlbWFpbCI6Im9wZXJhdG9yNEB0ZXN0LmNvbSIsInJvbGUiOiJvcGVyYXRvciJ9LCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzEyOTU3NTUyLCJpYXQiOjE3MTAzNjU1NTIsImp0aSI6IjM5ZGVkNjMxLWY4OTUtNDEzYi1iODNmLWQyYWI1YzlmZTAxNyJ9.ukhA0yJxnBUVdU9tFyM-s1eMmbtp4kv7anQYBZMmZeA",
        )

        # Wait for the server to respond
        event = await sio.receive()
        print(event)

        # Listen for chat messages
        send_msg_counter = 0
        await sio.emit("chat_listen", 4)
        while True:
            if send_msg_counter % 10 == 0:
                print(f"Sending message to 4: send_msg_counter: {send_msg_counter}")
                await sio.emit(
                    "chat_send",
                    {
                        "message": {
                            "to": 4,
                            "content": f"send_msg_counter: {send_msg_counter}",
                        }
                    },
                )
            try:
                event = await sio.receive(timeout=1)
            except Exception as e:
                print(e)
                send_msg_counter += 1
                continue
            if event[0] == "chat_message" and "message" in event[1]:
                print(event)
            if event[0] == "heartbeat":
                print("Reveived heartbeat")
            send_msg_counter += 1


if __name__ == "__main__":
    asyncio.run(run())
    sys.exit(0)
