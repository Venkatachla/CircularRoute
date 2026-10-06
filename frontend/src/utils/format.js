export const formatDate = (iso) =>
  iso
    ? new Date(iso).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })
    : "—";

export const formatTime = (iso) =>
  new Date(iso).toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

export const formatNumber = (n) => new Intl.NumberFormat("en-IN").format(n);

export const deptName = (code) => code || "—";

export const confidenceTone = (v) => (v >= 90 ? "success" : v >= 80 ? "warning" : "danger");

export const AUTO_THRESHOLD = 90;
