export namespace AuthDto {
  export interface Result {
    access_token: string;
  }

  export interface User {
    id: number;
    avatar_url: string | null;
    first_name: string | null;
    last_name: string | null;
  }

  export interface UserResult {
    id: number;
    first_name: string;
    last_name: string | null;
    avatar_url: string | null;
    unread_count: number;
    last_message_content: string;
    last_message_created_at: string;
  }
}
