import { observer } from "mobx-react-lite";
import { ChatVm } from "../../../../stores/chat.vm";
import { useState } from "react";
import ChevronIcon from "@/assets/icons/Chevron.svg";
import { cn } from "@/lib/utils";
import { MobileRecommendations } from "./MobileRecommendations";

export const Recommendations = observer(() => {
  const [docsHidden, setDocsHidden] = useState(false);

  return (
    <>
      <MobileRecommendations />
      <section className="hidden md:flex flex-col p-3 min-w-[300px] max-w-[300px] h-full overflow-hidden gap-2">
        <div className="flex flex-col w-full bg-white rounded-md max-h-full">
          <button
            className="flex gap-2 text-sm items-center sticky top-0 px-5 min-h-12"
            onClick={() => setDocsHidden(!docsHidden)}>
            Документы по теме
            <ChevronIcon className={cn("w-3", docsHidden && "rotate-180")} />
          </button>
          {!docsHidden && (
            <ul className="flex flex-col gap-3 w-full rounded-md px-3 pb-6 overflow-y-auto h-full relative">
              {ChatVm.docs.map((doc) => (
                <li
                  key={doc.id}
                  className="group p-1 px-2 hover:bg-slate-100 transition-colors rounded-lg">
                  <a href={doc.href} target="_blank">
                    <h3 className="text-[#3B86C6] text-sm font-medium group-hover:underline">
                      {doc.name}
                    </h3>
                    <p className="text-xs font-light">{doc.description}</p>
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </>
  );
});
