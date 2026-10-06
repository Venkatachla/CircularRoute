import { backendNotConfigured } from "./apiClient";

// GET /circulars
export async function listCirculars() {
  return [];
}

// GET /circulars/{id}
export async function getCircular(id) {
  throw new Error(`Circular ${id} was not found.`);
}

// GET /dashboard/summary
export async function getDashboard() {
  return { stats: [], volume: [], departments: [], confidence: [] };
}

// PATCH /circulars/{id}
export async function updateCircular(id, patch) {
  return backendNotConfigured();
}

// POST /circulars/{id}/approve | /reject
export async function decideCircular(id, decision) {
  return backendNotConfigured();
}

export async function uploadCircular(file) {
  return backendNotConfigured();
}
