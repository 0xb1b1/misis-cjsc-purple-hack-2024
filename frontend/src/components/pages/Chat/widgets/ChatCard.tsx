import { ChatDto } from "@/api/models/chat.model";
import { cn } from "@/lib/utils";
import { FC } from "react";
import { ChatVm } from "../../../../stores/chat.vm";
import { observer } from "mobx-react-lite";
import mockAvatar from "@/assets/img/mockAvatar.png";
// import { formatDistanceStrict } from "date-fns";
// import { ru } from "date-fns/locale";

export const ChatCard: FC<{ item: ChatDto.Short; onClick: () => void }> = observer((x) => {
  // const relativeTime = formatDistanceStrict(new Date(x.item.lastMessageTime), new Date(), {
  //   addSuffix: true,
  //   locale: ru
  // })
  //   .replace("часа назад", "ч")
  //   .replace("час назад", "ч")
  //   .replace("минут назад", "м")
  //   .replace("минуту назад", "м")
  //   .replace("секунд назад", "с");

  return (
    <div
      className={cn(
        "flex text-left p-2 gap-2 cursor-pointer rounded-lg transition-colors",
        ChatVm.selectedChat && x.item.id === ChatVm.selectedChat.id
          ? "bg-white"
          : "hover:bg-white/50"
      )}
      onClick={() => x.onClick()}>
      <img src={x.item.avatarSrc ?? mockAvatar} alt="Аватар" className="w-12 h-12 rounded-full" />
      <div className="flex flex-col w-full overflow-hidden">
        <h2 className="text-sm font-medium">
          {x.item.firstName} {x.item.lastName}
        </h2>
        <p className="text-xs font-light overflow-hidden whitespace-nowrap overflow-ellipsis w-full">
          {x.item.lastMessage}
        </p>
      </div>
      <div className="flex flex-col justify-between">
        <span className="text-text-secondary text-nowrap text-xs font-light">1 ч</span>
        {x.item.unreadCount > 0 && (
          <span className="bg-primary rounded-full text-[9px] text-white font-medium w-5 h-5 flex items-center justify-center">
            {x.item.unreadCount}
          </span>
        )}
      </div>
    </div>
  );
});
