import { makeAutoObservable } from "mobx";
import { ChatDto } from "@/api/models/chat.model";
import { DocDto } from "@/api/models/document.model";
import { GroupedMessages, MessageDto } from "@/api/models/message.model";
import { groupMessages } from "@/lib/utils";
import { AuthService } from "./auth.service";
import { MessageEndpoint } from "@/api/endpoints/message.endpoint";
import { SocketIoVm } from "./io.service";

const mockDocsList: DocDto.Short[] = new Array(32).fill({
  id: 1,
  href: "https://google.com/",
  name: "Документ",
  description: "Описание документа"
} satisfies DocDto.Short);

class ChatViewModel {
  chatList: ChatDto.Short[] = [];
  docs: DocDto.Short[] = mockDocsList;
  isOperator = false;
  private messagesDb: MessageDto.Short[] = [];
  selectedChat: ChatDto.Short | null = null;
  unsentMessage: MessageDto.Short | null = null;

  get messages(): GroupedMessages[] | null {
    if (!this.selectedChat) return null;

    const filtered = this.messagesDb.filter(
      (v) =>
        v.authorId === this.selectedChat!.id ||
        (AuthService.auth.state === "authenticated" && v.authorId === AuthService.auth.user.id)
    );

    return groupMessages([filtered, ...[this.unsentMessage ? [this.unsentMessage] : []]].flat());
  }

  constructor() {
    makeAutoObservable(this);
  }

  async init() {
    this.selectedChat = null;
    const chatList = await MessageEndpoint.getAll();
    this.isOperator = chatList.is_operator;
    if (this.isOperator && AuthService.auth.state === "authenticated") {
      AuthService.auth.user.id = 0;
    }
    this.chatList = Object.values(chatList.users).map((v) => ({
      id: v.id,
      firstName: v.first_name,
      lastName: v.last_name,
      avatarSrc: v.avatar_url,
      unreadCount: v.unread_count,
      lastMessage: v.last_message_content,
      lastMessageTime: v.last_message_created_at
    }));

    if (!this.isOperator) {
      this.selectedChat = {
        id: 0,
        firstName: "Оператор",
        lastName: null,
        avatarSrc: null,
        unreadCount: 0,
        lastMessage: "",
        lastMessageTime: ""
      };
    }
  }

  selectChat(id: number | null) {
    if (id !== null && !isNaN(id)) {
      this.selectedChat = this.chatList.find((chat) => chat.id === id) || null;

      if (this.selectedChat) {
        this.selectedChat.unreadCount = 0;
      }
    }
  }

  onMessage(message: MessageDto.Short) {
    if (message.authorId !== this.selectedChat?.id) {
      const chat = this.chatList.find((chat) => chat.id === message.authorId);
      if (chat) {
        chat.unreadCount++;
        chat.lastMessage = message.message;
      }
    }

    if (this.messagesDb.find((v) => v.id === message.id)) return;
    this.messagesDb.push(message);
  }

  messageText = "";
  async sendMessage() {
    if (AuthService.auth.state !== "authenticated") return;
    if (!this.messageText.trim()) return;

    // this.unsentMessage = {
    //   id: -1,
    //   authorId: AuthService.auth.user.id,
    //   message: this.messageText
    // };

    SocketIoVm.sendMessage(this.selectedChat!.id, this.messageText);

    this.messageText = "";
  }
}

export const ChatVm = new ChatViewModel();
