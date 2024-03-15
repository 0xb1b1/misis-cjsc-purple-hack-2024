/* eslint-disable react-hooks/exhaustive-deps */
import { observer } from "mobx-react-lite";
import { MessageForm } from "../widgets/MessageForm";
import { ChatVm } from "@/stores/chat.vm";
import { MessageCard } from "../widgets/MessageCard";
import { useEffect, useRef } from "react";

export const Chat = observer(() => {
  const chatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [ChatVm.messages]);
  return (
    <section className="w-full flex flex-col overflow-hidden lg:border-x lg:border-x-[#E4E4E4]">
      <div
        ref={chatRef}
        className="flex flex-col-reverse w-full flex-1 overflow-y-auto overflow-x-hidden px-2 pt-8">
        {ChatVm.messages ? (
          <div className="flex flex-col gap-6">
            {ChatVm.messages.map((item, index) => (
              <MessageCard key={index} item={item} />
            ))}
          </div>
        ) : (
          <div className="h-full w-full flex items-center justify-center">
            <h1 className="text-2xl text-text-secondary">Выберите чат</h1>
          </div>
        )}
      </div>
      <div className="m-2">
        <MessageForm />
      </div>
    </section>
  );
});
