import { FileText, ExternalLink, AlertCircle } from "lucide-react";

export default function DocumentPreview({ circular }) {
  const hasUrl = Boolean(circular?.documentUrl);
  const filename = circular?.filename || (circular?.id ? `Circular ${circular.id}` : "circular");

  if (!hasUrl) {
    return (
      <div className="card-surface flex items-center justify-between gap-4 p-4 text-sm text-muted-foreground">
        <div className="flex items-center gap-2.5">
          <AlertCircle className="size-4 text-warning" />
          <span>Original circular document unavailable</span>
        </div>
      </div>
    );
  }

  return (
    <div className="card-surface flex flex-wrap items-center justify-between gap-3 p-4 text-sm">
      <div className="flex items-center gap-3 min-w-0">
        <span className="flex size-8 shrink-0 items-center justify-center rounded-md bg-brand-soft text-brand">
          <FileText className="size-4" />
        </span>
        <div className="truncate">
          <span className="font-semibold text-foreground">Original circular: </span>
          <span className="font-mono text-muted-foreground">{filename}</span>
        </div>
      </div>
      <a
        href={circular.documentUrl}
        target="_blank"
        rel="noopener noreferrer"
        aria-label={`Open original circular ${filename} in new tab`}
        className="inline-flex shrink-0 items-center gap-1.5 rounded-md border border-input bg-card px-3 py-1.5 text-xs font-semibold text-foreground transition hover:bg-surface hover:text-brand"
      >
        <span>View circular</span>
        <ExternalLink className="size-3.5" />
      </a>
    </div>
  );
}
