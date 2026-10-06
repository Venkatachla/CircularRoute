import { backendNotConfigured } from "./apiClient";

// GET /directory
export async function listDirectory() {
  return [];
}

// POST /recipients/resolve  { phrase, departments, roles }
export async function resolveRecipients({ phrase, departments = [], roles = [] }) {
  return backendNotConfigured();
}
