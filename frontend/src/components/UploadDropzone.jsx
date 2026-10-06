import { useRef, useState } from "react";
import { motion } from "motion/react";
import { UploadCloud, FileText, FileType2, Image as ImageIcon, FileCheck2 } from "lucide-react";
import { cn } from "@/lib/utils";

const ACCEPT = ".pdf,.docx,.png,.jpg,.jpeg,.tiff";

export default function UploadDropzone({ onFile, disabled }) {
  const input = useRef(null);
  const [over, setOver] = useState(false);

  const pick = (files) => {
    const f = files?.[0];
    if (f) onFile(f);
  };

  return (
    <motion.div
      role="button"
      tabIndex={0}
      aria-label="Upload a circular. Drop a document or press Enter to browse files."
      onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && input.current?.click()}
      onClick={() => !disabled && input.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setOver(true); }}
      onDragLeave={() => setOver(false)}
      onDrop={(e) => { e.preventDefault(); setOver(false); pick(e.dataTransfer.files); }}
      animate={{ scale: over ? 1.005 : 1 }}
      className={cn(
        "grid-dots relative flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-14 text-center transition-colors",
        over ? "border-brand bg-brand-soft" : "border-input bg-card hover:border-brand/60",
        disabled && "pointer-events-none opacity-60",
      )}
    >
      <input ref={input} type="file" accept={ACCEPT} className="sr-only" onChange={(e) => pick(e.target.files)} />
      <motion.div
        animate={{ y: over ? -4 : 0 }}
        className="mb-5 flex size-14 items-center justify-center rounded-xl border bg-card shadow-[var(--shadow-lift)]"
      >
        <UploadCloud className="size-6 text-brand" />
      </motion.div>
      <h2 className="text-lg font-semibold tracking-tight">Upload a circular</h2>
      <p className="mt-1 text-sm text-muted-foreground">
        Drop your document here or <span className="font-medium text-brand underline-offset-4 hover:underline">browse files</span>
      </p>
      <div className="mt-6 flex flex-wrap justify-center gap-2">
        {[
          { icon: FileText, l: "PDF" }, { icon: FileType2, l: "DOCX" }, { icon: ImageIcon, l: "Images" }, { icon: FileCheck2, l: "Digital documents" },
        ].map(({ icon: I, l }) => (
          <span key={l} className="inline-flex items-center gap-1.5 rounded-md border bg-card px-2.5 py-1 text-xs text-muted-foreground">
            <I className="size-3.5" /> {l}
          </span>
        ))}
      </div>
      <p className="mt-4 text-xs text-muted-foreground">Maximum 25 MB · Encrypted in transit</p>
    </motion.div>
  );
}
