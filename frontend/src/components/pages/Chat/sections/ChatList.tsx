import { observer } from "mobx-react-lite";
import { ChatVm } from "../../../../stores/chat.vm";
import { ChatCard } from "../widgets/ChatCard";
import { cn } from "@/lib/utils";
import { useState } from "react";
import ChevronIcon from "@/assets/icons/Chevron.svg";

export const ChatList = observer(() => {
  const [hidden, setHidden] = useState(false);

  if (!ChatVm.isOperator) return null;

  return (
    <>
      <section
        className={cn(
          "flex h-full top-0 left-0 bottom-0 lg:relative min-w-[324px] max-w-[324px] gap-1",
          "absolute transform transition-transform lg:translate-x-0",
          hidden ? "-translate-x-[324px]" : "translate-x-0"
        )}>
        <div
          className={cn(
            "bg-bg flex flex-col px-3 min-w-[324px] max-w-[324px] shadow-lg lg:shadow-none overflow-hidden",
            hidden && "shadow-none"
          )}
          style={{ maxHeight: "calc(100vh - 40px)" }}>
          <h1 className="font-medium text-4xl pt-6">Чаты</h1>
          <ul className="flex flex-col overflow-auto min-w-[200px] max-w-[300px] mt-6 ">
            {ChatVm.chatList.map((chat, i) => (
              <li key={i}>
                <ChatCard
                  item={chat}
                  onClick={() => {
                    setHidden(true);
                    ChatVm.selectChat(chat.id);
                  }}
                />
              </li>
            ))}
          </ul>
        </div>
      </section>
      <button
        className={cn(
          "w-8 h-12 items-center justify-center absolute left-[328px] top-4 bg-white rounded-xl shadow-md transition-all lg:hidden flex",
          hidden && "left-2"
        )}
        onClick={() => setHidden(!hidden)}>
        <ChevronIcon className={cn("w-5 h-5", hidden ? "rotate-90" : "-rotate-90")} />
      </button>
    </>
  );
});
