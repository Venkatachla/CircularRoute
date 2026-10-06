import { FileX2, AlertOctagon, RotateCw } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";

export function EmptyState({ icon: Icon = FileX2, title, body, action }) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
      <div className="grid-dots mb-4 flex size-14 items-center justify-center rounded-xl border bg-card">
        <Icon className="size-6 text-muted-foreground" />
      </div>
      <h3 className="text-sm font-semibold">{title}</h3>
      {body && <p className="mt-1 max-w-sm text-sm text-muted-foreground">{body}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function ErrorState({ error, onRetry }) {
  return (
    <div role="alert" className="flex flex-col items-center justify-center px-6 py-16 text-center">
      <div className="mb-4 flex size-12 items-center justify-center rounded-xl bg-danger-soft">
        <AlertOctagon className="size-5 text-danger" />
      </div>
      <h3 className="text-sm font-semibold">Unable to load data</h3>
      <p className="mt-1 text-sm text-muted-foreground">{error?.message || "The service did not respond."}</p>
      {onRetry && (
        <Button variant="outline" size="sm" className="mt-4" onClick={onRetry}>
          <RotateCw className="size-3.5" /> Retry
        </Button>
      )}
    </div>
  );
}

export function SkeletonRows({ rows = 6 }) {
  return (
    <div className="space-y-3 p-5" aria-busy="true" aria-label="Loading">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-4">
          <Skeleton className="h-4 flex-1" />
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-4 w-16" />
        </div>
      ))}
    </div>
  );
}
