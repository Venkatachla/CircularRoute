import { useState } from "react";
import { Pencil, Check } from "lucide-react";
import { toast } from "sonner";
import { ConfidenceRing, ConfidenceBar } from "./ConfidenceScore";
import { deptName } from "@/utils/format";
import { updateCircular } from "@/services/circularService";

function Field({ label, value, onSave, multiline }) {
  const [editing, setEditing] = useState(false);
  const [v, setV] = useState(value);
  const Tag = multiline ? "textarea" : "input";
  return (
    <div className="group border-b py-3 last:border-0">
      <div className="mb-1 flex items-center justify-between">
        <label className="label-caps">{label}</label>
        <button
          aria-label={editing ? `Save ${label}` : `Edit ${label}`}
          onClick={() => { if (editing) onSave(v); setEditing(!editing); }}
          className="rounded p-1 text-muted-foreground opacity-0 transition hover:bg-muted group-hover:opacity-100 focus:opacity-100"
        >
          {editing ? <Check className="size-3.5 text-success" /> : <Pencil className="size-3.5" />}
        </button>
      </div>
      {editing ? (
        <Tag
          autoFocus value={v} onChange={(e) => setV(e.target.value)} rows={3}
          className="w-full rounded-md border border-input bg-card px-2.5 py-1.5 text-sm focus:border-brand focus:outline-none"
        />
      ) : (
        <div className="text-sm text-foreground">{v || <span className="text-muted-foreground">Not detected</span>}</div>
      )}
    </div>
  );
}

function Chips({ items }) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((i) => <span key={i} className="rounded-md border bg-surface px-2 py-0.5 text-xs">{i}</span>)}
    </div>
  );
}

export default function ExtractionPanel({ circular }) {
  const save = (key) => async (val) => {
    await updateCircular(circular.id, { [key]: val });
    toast.success("Field updated", { description: "Change recorded in the audit log." });
  };
  const fc = circular.fieldConfidence || {};
  return (
    <div className="space-y-4">
      <div className="card-surface flex flex-col items-center gap-6 p-5 sm:flex-row">
        <ConfidenceRing value={circular.confidence} label="Extraction" />
        <div className="w-full flex-1 space-y-3">
          <div className="text-sm font-semibold">AI Extraction Confidence</div>
          {Object.entries(fc).map(([k, v]) => <ConfidenceBar key={k} label={k} value={v} />)}
        </div>
      </div>
      <div className="card-surface px-5 py-1">
        <Field label="Subject" value={circular.title} onSave={save("title")} />
        <Field label="Issuing Authority" value={circular.authority} onSave={save("authority")} />
        <div className="grid grid-cols-2 gap-x-6">
          <Field label="Reference Number" value={circular.ref} onSave={save("ref")} />
          <Field label="Date" value={new Date(circular.date).toLocaleDateString("en-IN")} onSave={() => {}} />
        </div>
        <div className="border-b py-3">
          <div className="label-caps mb-1.5">Departments</div>
          <Chips items={circular.departments.map(deptName)} />
        </div>
        <div className="border-b py-3">
          <div className="label-caps mb-1.5">Designations / Roles</div>
          <Chips items={circular.roles} />
        </div>
        <Field label="Recipients" value={circular.recipientPhrase} onSave={save("recipientPhrase")} />
        <Field label="Instructions / Actions" value={circular.instructions} onSave={save("instructions")} multiline />
        <div className="grid grid-cols-2 gap-x-6">
          <Field label="Deadline" value={circular.deadline} onSave={save("deadline")} />
          <Field label="Urgency" value={circular.urgency} onSave={save("urgency")} />
        </div>
      </div>
    </div>
  );
}
