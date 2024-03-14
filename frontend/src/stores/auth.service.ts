import { AuthEndpoint } from "@/api/endpoints/auth.endpoint";
import { getStoredAuthToken, removeStoredAuthToken } from "@/api/utils/authToken";
import { makeAutoObservable } from "mobx";
import { SocketIoVm } from "./io.service";
import { ChatVm } from "./chat.vm";

type Auth =
  | {
      state: "loading" | "anonymous";
    }
  | {
      state: "authenticated";
      user: {
        id: number;
      };
    };

class AuthServiceViewModel {
  public auth: Auth = { state: "loading" };

  constructor() {
    makeAutoObservable(this);
    void this.init();
  }

  private async init() {
    try {
      const user = await AuthEndpoint.getMe();
      this.auth = { state: "authenticated", user };
      await ChatVm.init();
      SocketIoVm.init(getStoredAuthToken()!);
    } catch {
      this.auth = { state: "anonymous" };
    }
  }

  login = async (username: string, password: string): Promise<boolean> => {
    try {
      await AuthEndpoint.login(username, password);

      const user = await AuthEndpoint.getMe();
      this.auth = { state: "authenticated", user };
      await ChatVm.init();
      SocketIoVm.init(getStoredAuthToken()!);
      return true;
    } catch {
      return false;
    }
  };

  logout() {
    this.auth = { state: "anonymous" };
    SocketIoVm.disconnect();
    removeStoredAuthToken();
  }
}

export const AuthService = new AuthServiceViewModel();
