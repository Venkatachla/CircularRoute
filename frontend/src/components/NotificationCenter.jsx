import { Bell } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

export default function NotificationCenter() {
  const unread = 0;
  return (
    <Popover>
      <PopoverTrigger asChild>
        <button aria-label={`Notifications, ${unread} unread`} className="relative rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground">
          <Bell className="size-[18px]" />
          {unread > 0 && <span className="absolute right-1.5 top-1.5 size-2 rounded-full bg-brand ring-2 ring-card" />}
        </button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-[360px] p-0">
        <div className="flex items-center justify-between border-b px-4 py-3">
          <span className="text-sm font-semibold">Notifications</span>
        </div>
        <ul className="max-h-96 divide-y overflow-y-auto">
          <li className="px-4 py-6 text-center text-sm text-muted-foreground">No notifications.</li>
        </ul>
      </PopoverContent>
    </Popover>
  );
}
