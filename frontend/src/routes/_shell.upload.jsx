import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import PageHeader from "@/components/PageHeader";
import UploadDropzone from "@/components/UploadDropzone";

export const Route = createFileRoute("/_shell/upload")({
  head: () => ({
    meta: [
      { title: "Upload Circular — CircularRoute" },
      { name: "description", content: "Upload a circular for AI extraction and automatic routing." },
      { property: "og:title", content: "Upload Circular — CircularRoute" },
      { property: "og:description", content: "Upload a circular for AI extraction and automatic routing." },
    ],
  }),
  component: Upload,
});

function Upload() {
  const [file, setFile] = useState(null);

  return (
    <>
      <PageHeader eyebrow="Ingest" title="Upload circular" subtitle="Select a PDF, DOCX or scanned image." />
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-4">
          <UploadDropzone onFile={setFile} />
          {file && <div className="card-surface p-4 text-sm"><span className="label-caps">File</span><div className="mt-1 font-mono">{file.name} · {Math.round(file.size / 1024)} KB</div></div>}
        </div>
        <div className="card-surface p-5">
          <div className="label-caps mb-4">Processing</div>
          <p className="text-sm text-muted-foreground">Upload processing will be available after backend integration.</p>
        </div>
      </div>
    </>
  );
}
