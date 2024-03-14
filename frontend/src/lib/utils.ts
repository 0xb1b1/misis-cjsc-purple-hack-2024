import { GroupedMessages, MessageDto } from "@/api/models/message.model";
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function groupMessages(messages: MessageDto.Short[]): GroupedMessages[] {
  const grouped: GroupedMessages[] = [];

  messages.forEach((message) => {
    const lastGroup = grouped[grouped.length - 1];

    // Если последняя группа существует и автор последнего сообщения в группе совпадает с автором текущего сообщения
    if (lastGroup && lastGroup.authorId === message.authorId) {
      lastGroup.messages.push(message);
    } else {
      // Если автор не совпадает или это первое сообщение, начинаем новую группу
      grouped.push({
        authorId: message.authorId,
        messages: [message]
      });
    }
  });

  return grouped;
}
