import { cn } from "@/lib/utils";
import avatarSrc from "./assets/cat.png";
import ChatIcon from "./assets/chat.svg";
import HomeIcon from "./assets/home.svg";
import Logo from "./assets/logo.svg";
import LogoutIcon from "@/assets/icons/Logout.svg";
import { AuthService } from "@/stores/auth.service";

export const Sidebar = () => {
  return (
    <aside
      className={cn(
        "md:h-full md:w-20 xl:w-36 flex md:flex-col items-center py-2 px-4 md:px-0 md:py-10 justify-between"
      )}>
      <Logo className="w-12 md:w-14" />
      <nav>
        <ul className="flex md:flex-col gap-8 *:cursor-pointer *:p-2">
          <li>
            <ChatIcon className="w-6 md:w-10" />
          </li>
          <li>
            <a href="https://cbr.ru/" target="_blank">
              <HomeIcon className="w-6 md:w-10" />
            </a>
          </li>
        </ul>
      </nav>
      <div className="flex flex-col items-center gap-4">
        <button className="w-6 md:w-10 ml-1.5" onClick={() => AuthService.logout()}>
          <LogoutIcon />
        </button>
        <img src={avatarSrc} className="hidden md:block w-12 h-12 object-cover rounded-full" />
      </div>
    </aside>
  );
};
