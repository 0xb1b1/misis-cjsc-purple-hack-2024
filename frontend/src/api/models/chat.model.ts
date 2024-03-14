export namespace ChatDto {
  export interface Short {
    id: number;
    firstName: string | null;
    lastName: string | null;
    avatarSrc: string | null;
    unreadCount: number;
    lastMessage: string;
    lastMessageTime: string;
  }
}
