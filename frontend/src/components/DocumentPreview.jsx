import { EmptyState } from "@/components/States";

export default function DocumentPreview({ circular }) {
  if (!circular.documentUrl) {
    return <EmptyState title="Document preview unavailable" body="A document preview will appear when a file is attached to this circular." />;
  }

  return (
    <iframe title="Circular document" src={circular.documentUrl} className="h-full w-full rounded-lg border bg-card" />
  );
}
