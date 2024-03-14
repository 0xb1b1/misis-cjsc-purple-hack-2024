import { observer } from "mobx-react-lite";
import { useState } from "react";
import DocIcon from "@/assets/icons/Doc.svg";
import { Drawer, DrawerContent, DrawerTitle, DrawerTrigger } from "@/components/ui/drawer";
import { ChatVm } from "@/stores/chat.vm";

export const MobileRecommendations = observer(() => {
  const [open, setOpen] = useState(false);

  return (
    <Drawer shouldScaleBackground open={open} onOpenChange={setOpen}>
      <DrawerTrigger className="md:hidden absolute w-12 h-12 top-4 right-2 flex items-center justify-center p-2.5 rounded-lg bg-white shadow-md">
        <DocIcon />
      </DrawerTrigger>
      <DrawerContent className="max-h-[80vh]">
        <DrawerTitle className="font-normal px-5 pb-4">Документы по теме</DrawerTitle>
        <ul className="flex flex-col gap-5 w-full rounded-md px-5 pb-6 overflow-y-auto h-full relative">
          {ChatVm.docs.map((doc) => (
            <li key={doc.id}>
              <a href={doc.href} target="_blank">
                <h3 className="text-[#3B86C6] text-lg font-medium">{doc.name}</h3>
                <p className="text-md font-light">{doc.description}</p>
              </a>
            </li>
          ))}
        </ul>
      </DrawerContent>
    </Drawer>
  );
});
