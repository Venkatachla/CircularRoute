import { Link } from "@tanstack/react-router";
import { motion } from "motion/react";
import { ChevronRight, FileText } from "lucide-react";
import StatusBadge from "./StatusBadge";
import ConfidenceScore from "./ConfidenceScore";
import { deptName, formatDate } from "@/utils/format";

export default function CircularTable({ circulars }) {
  return (
    <>
      {/* Desktop table */}
      <div className="hidden overflow-x-auto md:block">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left">
              {["Circular", "Reference No.", "Uploaded By", "Department", "Recipients", "Status", "Confidence", "Date", ""].map((h) => (
                <th key={h} className="label-caps whitespace-nowrap px-4 py-2.5 font-semibold first:pl-5">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {circulars.map((c, i) => (
              <motion.tr
                key={c.id}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03, duration: 0.2 }}
                className="group border-b last:border-0 transition-colors hover:bg-surface"
              >
                <td className="max-w-[320px] py-3 pl-5 pr-4">
                  <Link to="/circulars/$id" params={{ id: c.id }} className="flex items-center gap-3 font-medium text-foreground hover:text-brand">
                    <span className="flex size-8 shrink-0 items-center justify-center rounded-md border bg-surface"><FileText className="size-4 text-muted-foreground" /></span>
                    <span className="truncate">{c.title}</span>
                  </Link>
                </td>
                <td className="whitespace-nowrap px-4 font-mono text-xs text-muted-foreground">{c.ref}</td>
                <td className="whitespace-nowrap px-4">{c.uploadedBy}</td>
                <td className="whitespace-nowrap px-4 text-muted-foreground" title={deptName(c.dept)}>{c.dept}</td>
                <td className="tabular px-4">{c.recipients || "—"}</td>
                <td className="px-4"><StatusBadge status={c.status} /></td>
                <td className="px-4"><ConfidenceScore value={c.confidence} /></td>
                <td className="whitespace-nowrap px-4 text-muted-foreground">{formatDate(c.date)}</td>
                <td className="pr-4">
                  <Link to="/circulars/$id" params={{ id: c.id }} aria-label={`Open ${c.title}`} className="flex size-7 items-center justify-center rounded-md text-muted-foreground opacity-0 transition group-hover:opacity-100 hover:bg-muted focus:opacity-100">
                    <ChevronRight className="size-4" />
                  </Link>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* Mobile cards */}
      <ul className="divide-y md:hidden">
        {circulars.map((c) => (
          <li key={c.id}>
            <Link to="/circulars/$id" params={{ id: c.id }} className="block px-4 py-4 active:bg-surface">
              <div className="flex items-start justify-between gap-3">
                <span className="font-medium leading-snug">{c.title}</span>
                <StatusBadge status={c.status} />
              </div>
              <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
                <span className="font-mono">{c.ref}</span>
                <span>{c.dept}</span>
                <span>{formatDate(c.date)}</span>
                <ConfidenceScore value={c.confidence} />
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </>
  );
}
