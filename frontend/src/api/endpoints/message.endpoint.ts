import { AuthDto } from "api/models/auth.model";
import api from "api/utils/api";

export namespace MessageEndpoint {
  export const getAll = async () => {
    const result = await api.get<{ users: AuthDto.UserResult[]; is_operator: boolean }>(
      "/msg/chats"
    );

    return result;
  };
}
