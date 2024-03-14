import { SocketDto } from "@/api/models/socket.model";
import { makeAutoObservable } from "mobx";
import { io } from "socket.io-client";
import { ChatVm } from "./chat.vm";

class SocketIoViewModel {
  public io: ReturnType<typeof io> | null = null;

  constructor() {
    makeAutoObservable(this);
  }

  private hasConnected = false;
  init(token: string) {
    this.io = io("ws://localhost:8080/webapp", {
      transports: ["websocket"]
    });

    this.io.on("connect", () => {
      this.hasConnected = true;
      console.log("connected");
      this.io!.emit("auth", token);
      // this.io!.timeout(1000)
      //   .emitWithAck("auth", token)
      //   .then(() => console.log("ok"))
      //   .catch((e) => console.log(e));
      setTimeout(() => {
        this.io!.emit("chats_listen");

        this.io!.on("chat_message", (data: { message: SocketDto.ChatMessage }) => {
          ChatVm.onMessage({
            id: data.message.id,
            authorId: data.message.from,
            message: data.message.content
          });
        });

        this.io!.on("chats_listen", (data) => {
          console.log(data);
        });

        this.io!.on("heartbeat", () => {
          console.log("heartbeat");
        });
      }, 1000);
    });
  }

  sendMessage(to: number, message: string) {
    this.io!.emit("chat_send", {
      message: {
        to,
        content: message
      }
    });
  }

  disconnect() {
    console.log("disconnect");
    this.io?.disconnect();
  }
}

export const SocketIoVm = new SocketIoViewModel();
