import { createFileRoute } from "@tanstack/react-router";
import CircularWorkflow from "@/components/CircularWorkflow";

export const Route = createFileRoute("/_shell/")({
  head: () => ({ meta: [{ title: "Send a Circular — CircularRoute" }] }),
  component: CircularWorkflow,
});
