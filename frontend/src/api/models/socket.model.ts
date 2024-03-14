export namespace SocketDto {
  export interface ChatMessage {
    id: number;
    from: number;
    to: number;
    content: string;
  }
}
