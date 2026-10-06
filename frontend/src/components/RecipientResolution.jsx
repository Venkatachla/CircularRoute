import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Quote, ArrowDown, Check, X, ChevronDown, Mail, BadgeCheck } from "lucide-react";
import { cn } from "@/lib/utils";
import { deptName } from "@/utils/format";
import ConfidenceScore from "./ConfidenceScore";

export function RecipientCard({ person, index = 0 }) {
  const [open, setOpen] = useState(false);
  const ok = Object.values(person.checks).every(Boolean);
  return (
    <motion.li
      initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.04 }}
      className="rounded-lg border bg-card"
    >
      <button onClick={() => setOpen(!open)} aria-expanded={open} className="flex w-full items-center gap-3 p-3 text-left">
        <span className={cn("flex size-6 shrink-0 items-center justify-center rounded-full", ok ? "bg-success-soft text-success" : "bg-warning-soft text-warning")}>
          {ok ? <Check className="size-3.5" strokeWidth={2.5} /> : <X className="size-3.5" />}
        </span>
        <div className="min-w-0 flex-1">
          <div className="truncate text-sm font-medium">{person.name}</div>
          <div className="truncate text-xs text-muted-foreground">{person.role} · {person.dept}</div>
        </div>
        <span className="hidden items-center gap-1 font-mono text-xs text-muted-foreground sm:flex"><Mail className="size-3" />{person.email}</span>
        <ConfidenceScore value={person.confidence} />
        <ChevronDown className={cn("size-4 text-muted-foreground transition-transform", open && "rotate-180")} />
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.2 }} className="overflow-hidden">
            <div className="border-t bg-surface px-4 py-3">
              <div className="label-caps mb-2">Why was this person selected?</div>
              <ul className="grid gap-1.5 sm:grid-cols-2">
                {Object.entries(person.checks).map(([k, v]) => (
                  <li key={k} className="flex items-center gap-2 text-sm">
                    {v ? <Check className="size-4 text-success" /> : <X className="size-4 text-danger" />}
                    <span className={v ? "" : "text-muted-foreground"}>{k}</span>
                  </li>
                ))}
              </ul>
              <p className="mt-2 font-mono text-xs text-muted-foreground sm:hidden">{person.email}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.li>
  );
}

function Step({ n, title, children }) {
  return (
    <div className="card-surface p-5">
      <div className="mb-3 flex items-center gap-2">
        <span className="flex size-5 items-center justify-center rounded bg-primary font-mono text-[10px] font-semibold text-primary-foreground">{n}</span>
        <span className="label-caps">{title}</span>
      </div>
      {children}
    </div>
  );
}

const Arrow = () => <div className="flex justify-center py-1.5 text-muted-foreground"><ArrowDown className="size-4" /></div>;

export default function RecipientResolution({ data }) {
  const avg = data.recipients.length ? data.recipients.reduce((a, r) => a + r.confidence, 0) / data.recipients.length : 0;
  return (
    <div>
      <Step n="1" title="Extracted recipient">
        <div className="flex items-start gap-3">
          <Quote className="mt-0.5 size-4 shrink-0 text-brand" />
          <p className="text-lg font-medium tracking-tight">“{data.phrase}”</p>
        </div>
      </Step>
      <Arrow />
      <Step n="2" title="System interpretation">
        <dl className="grid gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-xs text-muted-foreground">Role</dt>
            <dd className="mt-1 flex flex-wrap gap-1.5">{data.interpretation.roles.map((r) => <span key={r} className="rounded-md bg-brand-soft px-2 py-0.5 text-sm font-medium text-brand">{r}</span>)}</dd>
          </div>
          <div>
            <dt className="text-xs text-muted-foreground">Department</dt>
            <dd className="mt-1 flex flex-wrap gap-1.5">{data.interpretation.departments.map((d) => <span key={d} className="rounded-md bg-surface px-2 py-0.5 text-sm font-medium border">{deptName(d)}</span>)}</dd>
          </div>
        </dl>
      </Step>
      <Arrow />
      <Step n="3" title={`Resolved recipients · ${data.recipients.length}`}>
        <div className="mb-3 flex items-center gap-2 text-xs text-muted-foreground">
          <BadgeCheck className="size-4 text-success" /> Average match confidence <ConfidenceScore value={Number(avg.toFixed(1))} />
        </div>
        <ul className="space-y-2">
          {data.recipients.map((p, i) => <RecipientCard key={p.id} person={p} index={i} />)}
        </ul>
      </Step>
    </div>
  );
}
