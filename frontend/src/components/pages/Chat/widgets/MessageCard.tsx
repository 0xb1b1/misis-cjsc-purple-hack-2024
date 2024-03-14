import { GroupedMessages } from "@/api/models/message.model";
import { cn } from "@/lib/utils";
import { AuthService } from "@/stores/auth.service";
import { ChatVm } from "@/stores/chat.vm";
import { observer } from "mobx-react-lite";
import { FC } from "react";
import mockAvatar from "@/assets/img/mockAvatar.png";

export const MessageCard: FC<{ item: GroupedMessages }> = observer((x) => {
  if (AuthService.auth.state !== "authenticated") return null;
  const userId = AuthService.auth.user.id;

  const isAuthor = x.item.authorId === userId;

  return (
    <div className="flex items-end w-full gap-6">
      {!isAuthor && (
        <img
          src={ChatVm.selectedChat?.avatarSrc ?? mockAvatar}
          className="rounded-full w-12 h-12 min-w-12"
          alt="Аватар"
        />
      )}
      <div className={cn("flex flex-col max-w-[450px]  gap-2 font-light", isAuthor && "ml-auto")}>
        {x.item.messages.map((message, index) => (
          <div
            key={index}
            style={{
              borderTopRightRadius: isAuthor && index !== 0 ? 0 : "12px",
              borderTopLeftRadius: !isAuthor && 0 !== index ? 0 : "12px",
              borderBottomLeftRadius:
                !isAuthor && index !== x.item.messages.length - 1 ? 0 : "12px",
              borderBottomRightRadius: isAuthor && x.item.messages.length - 1 !== index ? 0 : "12px"
            }}
            className={cn(
              "py-2 px-4",
              isAuthor ? "bg-primary text-white" : "bg-white",
              x.item.messages.length === 1 && "!rounded-xl"
            )}>
            {message.message}
          </div>
        ))}
      </div>
    </div>
  );
});
