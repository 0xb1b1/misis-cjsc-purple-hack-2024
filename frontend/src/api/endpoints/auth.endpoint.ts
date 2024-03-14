import { AuthDto } from "api/models/auth.model";
import api from "api/utils/api";
import { setStoredAuthToken } from "api/utils/authToken";
import { parseJwt } from "api/utils/parseJwt";

export namespace AuthEndpoint {
  export const login = async (username: string, password: string) => {
    const result = await api.post<AuthDto.Result>("/auth/login", {
      email: username,
      password
    });

    setStoredAuthToken(result.access_token);
    return parseJwt(result.access_token);
  };

  export const getMe = async () => {
    const result = await api.get<AuthDto.User>("/auth/me/full");

    return result;
  };
}
