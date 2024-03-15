#!/usr/bin/env python3
import sys

# from time import sleep
# import asyncio
import socketio


def run():
    # asyncio
    with socketio.SimpleClient() as sio:
        sio.connect("http://127.0.0.1:8080", namespace="/webapp")
        # Authenticate with JWT TOKEN
        sio.emit(
            "auth",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWJqZWN0Ijp7ImlkIjowLCJlbWFpbCI6Im9wZXJhdG9yNEB0ZXN0LmNvbSIsInJvbGUiOiJvcGVyYXRvciJ9LCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzEyOTU4OTA4LCJpYXQiOjE3MTAzNjY5MDgsImp0aSI6IjYxYTQzZmQ0LTRkZGMtNGRjMy1hYWZjLWQxZDk4YzhkNWVmMyJ9.sNjKb9YJZVPw4bk7da81yIG8f5DMJargQ_99r_ZTkkY",
        )

        # Wait for the server to respond
        event = sio.receive()
        print(event)

        # Get chats list
        sio.emit("chats_list")
        chat_list = sio.receive()
        print(chat_list)

        # Listen for chat messages
        send_msg_counter = 0
        sio.emit("chats_listen")
        while True:
            if send_msg_counter % 10 == 0:
                print(f"Sending message to 4: send_msg_counter: {send_msg_counter}")
                sio.emit(
                    "chat_send",
                    {
                        "message": {
                            "to": 4,
                            "content": f"send_msg_counter: {send_msg_counter}",
                        }
                    },
                )
            try:
                event = sio.receive(timeout=1)
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
    run()
    sys.exit(0)
