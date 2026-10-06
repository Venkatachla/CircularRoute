import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import PageHeader from "@/components/PageHeader";
import { Switch } from "@/components/ui/switch";

export const Route = createFileRoute("/_shell/settings")({
  head: () => ({
    meta: [
      { title: "Settings — CircularRoute" },
      { name: "description", content: "Configure thresholds, notifications and integrations." },
      { property: "og:title", content: "Settings — CircularRoute" },
      { property: "og:description", content: "Configure thresholds, notifications and integrations." },
    ],
  }),
  component: Settings,
});

function Settings() {
  const [threshold, setThreshold] = useState(90);
  const [opts, setOpts] = useState({ auto: true, digest: true, failures: true });
  const row = (k, label, desc) => (
    <div className="flex items-center justify-between gap-4 py-3">
      <div><div className="text-sm font-medium">{label}</div><div className="text-xs text-muted-foreground">{desc}</div></div>
      <Switch checked={opts[k]} onCheckedChange={(v) => setOpts({ ...opts, [k]: v })} />
    </div>
  );
  return (
    <>
      <PageHeader eyebrow="System" title="Settings" />
      <div className="grid max-w-3xl gap-6">
        <div className="card-surface p-5">
          <div className="label-caps mb-3">Decision engine</div>
          <label className="text-sm font-medium">Auto-distribution threshold: <span className="tabular text-brand">{threshold}%</span></label>
          <input type="range" min={70} max={99} value={threshold} onChange={(e) => setThreshold(+e.target.value)} className="mt-2 w-full accent-[var(--brand)]" />
          <div className="divide-y">{row("auto", "Auto-distribute high confidence", "Send without human review above the threshold.")}</div>
        </div>
        <div className="card-surface p-5">
          <div className="label-caps mb-1">Notifications</div>
          <div className="divide-y">
            {row("digest", "Daily digest", "Summary email to administrators at 6 PM.")}
            {row("failures", "Delivery failure alerts", "Notify immediately when emails bounce.")}
          </div>
        </div>
        <button onClick={() => toast.success("Settings saved")} className="h-9 w-fit rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground">Save changes</button>
      </div>
    </>
  );
}
