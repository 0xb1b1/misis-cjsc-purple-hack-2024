export namespace MessageDto {
  export interface Short {
    id: number;
    authorId: number;
    message: string;
  }

  export interface Result {}
}

export interface GroupedMessages {
  authorId: number;
  messages: MessageDto.Short[];
}
