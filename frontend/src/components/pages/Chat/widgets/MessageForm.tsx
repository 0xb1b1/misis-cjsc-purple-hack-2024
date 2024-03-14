import { observer } from "mobx-react-lite";
import PlusSvg from "@/assets/icons/Plus.svg";
import SendSvg from "@/assets/icons/Send.svg";
import { ChatVm } from "../../../../stores/chat.vm";
import { cn } from "@/lib/utils";

export const MessageForm = observer(() => {
  const disabled = ChatVm.unsentMessage !== null || ChatVm.selectedChat === null;
  return (
    <form
      className={cn(
        "flex items-center w-full p-2 gap-2 bg-white rounded-md transition-opacity",
        disabled && "opacity-50"
      )}
      onSubmit={(e) => {
        e.preventDefault();
        if (disabled) return;
        ChatVm.sendMessage();
      }}>
      <button
        className="bg-[#D8E7F4] rounded-md w-12 h-12 md:w-8 md:h-8 flex items-center justify-center hover:brightness-105"
        type="button">
        <PlusSvg />
      </button>
      <input
        type="text"
        onChange={(e) => (ChatVm.messageText = e.target.value)}
        placeholder="Сообщение..."
        value={ChatVm.messageText}
        disabled={disabled}
        className={cn(
          "font-light outline-none flex-1 h-14 md:h-8 px-2 rounded-lg bg-transparent",
          " transition-colors"
        )}
      />
      <button
        className={cn(
          "w-12 h-12 md:w-8 md:h-8 bg-primary rounded-md flex items-center justify-center hover:brightness-125"
        )}
        disabled={disabled}>
        <SendSvg />
      </button>
    </form>
  );
});
