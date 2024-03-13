#!/usr/bin/env python3
import sys
import asyncio
import socketio


async def run():
    # asyncio
    async with socketio.AsyncSimpleClient() as sio:
        await sio.connect("http://127.0.0.1:8080", namespace="/webapp")
        # Authenticate with JWT TOKEN
        await sio.emit("auth", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWJqZWN0Ijp7ImlkIjoxLCJlbWFpbCI6InUwQGV4YW1wbGUuY29tIiwicm9sZSI6InVzZXIifSwidHlwZSI6ImFjY2VzcyIsImV4cCI6MTcxMjg2ODk2MSwiaWF0IjoxNzEwMjc2OTYxLCJqdGkiOiJhNDQ5MjUwNi02OGVhLTQ4YTMtOTlmMy0wMmZhZWYwZmY0NTAifQ.rQYU4ImwpbqA9-lT4vwj_W_lxmsmWuHlIJArZvp5vc0")

        # Wait for the server to respond
        event = await sio.receive()
        print(event)

        # Get chats list
        await sio.emit("chats_list")
        chat_list = await sio.receive()
        print(chat_list)

        # Listen for chat messages
        send_msg_counter = 0
        await sio.emit("chats_listen")
        while True:
            if send_msg_counter % 10 == 0:
                print(f"Sending message to 4: send_msg_counter: {send_msg_counter}")
                await sio.emit("chat_send", {"message": {"to": 4, "content": f"send_msg_counter: {send_msg_counter}"}})
            try:
                event = await sio.receive(timeout=1)
            except Exception as e:
                print(e)
                send_msg_counter += 1
                continue
            if event[0] == "chat_message" and "message" in event[1]:
                print(event)
            if event[0] == "heartbeat":
                print("Received heartbeat")
            send_msg_counter += 1


if __name__ == "__main__":
    asyncio.run(run())
    sys.exit(0)
