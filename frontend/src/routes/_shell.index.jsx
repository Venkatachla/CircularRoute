import { createFileRoute, Link } from "@tanstack/react-router";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, CartesianGrid } from "recharts";
import { UploadCloud } from "lucide-react";
import PageHeader from "@/components/PageHeader";
import StatCard from "@/components/StatCard";
import CircularTable from "@/components/CircularTable";
import { EmptyState, ErrorState } from "@/components/States";
import { getDashboard, listCirculars } from "@/services/circularService";

export const Route = createFileRoute("/_shell/")({
  head: () => ({
    meta: [
      { title: "Overview — CircularRoute" },
      { name: "description", content: "Circular volume, approvals and delivery health at MSRIT." },
      { property: "og:title", content: "Overview — CircularRoute" },
      { property: "og:description", content: "Circular volume, approvals and delivery health at MSRIT." },
    ],
  }),
  loader: async () => ({ dash: await getDashboard(), circulars: await listCirculars() }),
  component: Overview,
  errorComponent: ({ error }) => <ErrorState error={error} />,
  notFoundComponent: () => <div>Not found</div>,
});

const tip = { contentStyle: { borderRadius: 8, border: "1px solid var(--border)", fontSize: 12 } };

function Overview() {
  const { dash, circulars } = Route.useLoaderData();
  return (
    <>
      <PageHeader eyebrow="Dashboard" title="Overview" subtitle="Institutional circular activity across MSRIT."
        actions={<Link to="/upload" className="inline-flex h-9 items-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground"><UploadCloud className="size-4" />Upload circular</Link>} />
      {dash.stats.length ? <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">{dash.stats.map((s) => <StatCard key={s.key} stat={s} />)}</div> : <EmptyState title="No dashboard data" body="Summary metrics will appear after backend integration." />}
      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <div className="card-surface p-5 lg:col-span-2">
          <div className="label-caps mb-4">Monthly circular volume</div>
          {dash.volume.length ? <div className="h-64"><ResponsiveContainer><AreaChart data={dash.volume}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
            <XAxis dataKey="m" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis fontSize={12} tickLine={false} axisLine={false} width={30} />
            <Tooltip {...tip} />
            <Area dataKey="v" name="Circulars" stroke="var(--brand)" fill="var(--brand-soft)" strokeWidth={2} />
          </AreaChart></ResponsiveContainer></div> : <p className="py-12 text-center text-sm text-muted-foreground">No activity data available.</p>}
        </div>
        <div className="card-surface p-5">
          <div className="label-caps mb-4">By department</div>
          {dash.departments.length ? <div className="h-64"><ResponsiveContainer><BarChart data={dash.departments} layout="vertical">
            <XAxis type="number" hide /><YAxis type="category" dataKey="dept" fontSize={12} tickLine={false} axisLine={false} width={40} />
            <Tooltip {...tip} /><Bar dataKey="v" name="Circulars" fill="var(--brand)" radius={[0, 4, 4, 0]} />
          </BarChart></ResponsiveContainer></div> : <p className="py-12 text-center text-sm text-muted-foreground">No department data available.</p>}
        </div>
      </div>
      <div className="mt-6">
        <div className="mb-3 flex items-center justify-between"><span className="label-caps">Recent circulars</span><Link to="/circulars" className="text-sm text-brand">View all</Link></div>
        {circulars.length ? <CircularTable circulars={circulars.slice(0, 6)} /> : <EmptyState title="No circulars yet" body="Uploaded circulars will appear here." />}
      </div>
    </>
  );
}
