import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import { Loader2, CheckCircle2, FileText, ArrowRight, AlertCircle } from "lucide-react";
import PageHeader from "@/components/PageHeader";
import UploadDropzone from "@/components/UploadDropzone";
import { uploadCircular } from "@/services/circularService";

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
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [step, setStep] = useState(0); // 0: Idle, 1: Uploading, 2: OCR Parsing, 3: Completed
  const [errorMsg, setErrorMsg] = useState(null);

  const handleFileSelect = async (selectedFile) => {
    setFile(selectedFile);
    setUploading(true);
    setStep(1);
    setErrorMsg(null);

    try {
      // Step 1: Uploading
      setStep(2); // Running PaddleOCR & TrOCR
      const res = await uploadCircular(selectedFile);

      setStep(3); // Complete
      toast.success("Circular processed successfully!", {
        description: `Document ID: ${res.document_id}`,
      });

      setTimeout(() => {
        navigate({ to: "/circulars/$id", params: { id: res.document_id } });
      }, 1000);
    } catch (err) {
      setErrorMsg(err.message || "Failed to process circular.");
      toast.error("Processing failed", { description: err.message });
      setUploading(false);
      setStep(0);
    }
  };

  return (
    <>
      <PageHeader eyebrow="Ingest" title="Upload circular" subtitle="Select a PDF or scanned circular image." />
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-4">
          <UploadDropzone onFile={handleFileSelect} disabled={uploading} />
          {file && (
            <div className="card-surface p-4 text-sm flex items-center justify-between">
              <div>
                <span className="label-caps">Selected File</span>
                <div className="mt-1 font-mono font-medium flex items-center gap-2">
                  <FileText className="size-4 text-brand" />
                  {file.name} · {Math.round(file.size / 1024)} KB
                </div>
              </div>
              {uploading && <Loader2 className="size-5 animate-spin text-brand" />}
            </div>
          )}
          {errorMsg && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800 dark:border-red-900/50 dark:bg-red-950/30 dark:text-red-300 flex items-center gap-2">
              <AlertCircle className="size-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}
        </div>
        <div className="card-surface p-6 space-y-6">
          <div className="label-caps">Processing Pipeline</div>

          <div className="space-y-4">
            <div className={`flex items-start gap-3 rounded-lg border p-3.5 transition ${step >= 1 ? "border-brand bg-brand-soft/30" : "border-border"}`}>
              <div className="mt-0.5">
                {step > 1 ? (
                  <CheckCircle2 className="size-5 text-success" />
                ) : step === 1 ? (
                  <Loader2 className="size-5 animate-spin text-brand" />
                ) : (
                  <span className="flex size-5 items-center justify-center rounded-full border text-xs text-muted-foreground">1</span>
                )}
              </div>
              <div>
                <div className="text-sm font-medium">1. Document Upload & Registration</div>
                <div className="text-xs text-muted-foreground">Registers circular document and prepares high-resolution render frames.</div>
              </div>
            </div>

            <div className={`flex items-start gap-3 rounded-lg border p-3.5 transition ${step >= 2 ? "border-brand bg-brand-soft/30" : "border-border"}`}>
              <div className="mt-0.5">
                {step > 2 ? (
                  <CheckCircle2 className="size-5 text-success" />
                ) : step === 2 ? (
                  <Loader2 className="size-5 animate-spin text-brand" />
                ) : (
                  <span className="flex size-5 items-center justify-center rounded-full border text-xs text-muted-foreground">2</span>
                )}
              </div>
              <div>
                <div className="text-sm font-medium">2. OCR & Copy-to Section Extraction</div>
                <div className="text-xs text-muted-foreground">PaddleOCR printed text recognition & Microsoft TrOCR handwriting parsing.</div>
              </div>
            </div>

            <div className={`flex items-start gap-3 rounded-lg border p-3.5 transition ${step >= 3 ? "border-brand bg-brand-soft/30" : "border-border"}`}>
              <div className="mt-0.5">
                {step === 3 ? (
                  <CheckCircle2 className="size-5 text-success" />
                ) : (
                  <span className="flex size-5 items-center justify-center rounded-full border text-xs text-muted-foreground">3</span>
                )}
              </div>
              <div>
                <div className="text-sm font-medium">3. Copy-To Recipient Extraction</div>
                <div className="text-xs text-muted-foreground">Isolates and preserves printed and handwritten distribution recipients from the document.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
