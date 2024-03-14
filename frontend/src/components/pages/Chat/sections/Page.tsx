import { ChatList } from "./ChatList";
import { FC } from "react";
import { Chat } from "./Chat";
import { Recommendations } from "./Recommendations";
import { Sidebar } from "@/components/Sidebar/Sidebar";
import { observer } from "mobx-react-lite";

export const ChatPage: FC = observer(() => {
  return (
    <div className="flex flex-col md:flex-row h-dvh w-full appear">
      <Sidebar />
      <main className="md:py-5 md:pr-5 flex-1 flex w-full overflow-hidden">
        <div className="bg-bg w-full h-full rounded-xl flex relative overflow-hidden">
          <ChatList />
          <Chat />
          <Recommendations />
        </div>
      </main>
    </div>
  );
});
