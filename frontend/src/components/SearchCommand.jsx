import { useEffect } from "react";
import { CommandDialog, CommandInput, CommandList, CommandEmpty } from "@/components/ui/command";

export default function SearchCommand({ open, setOpen }) {
  useEffect(() => {
    const onKey = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((o) => !o);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [setOpen]);

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Search circulars, recipients, departments, audit logs…" />
      <CommandList>
        <CommandEmpty>No records are available to search.</CommandEmpty>
      </CommandList>
    </CommandDialog>
  );
}
