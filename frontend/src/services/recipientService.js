/**
 * Recipient service (legacy resolution decoupled).
 * CircularRoute now delegates recipient matching and email resolution to downstream services.
 */
export async function listDirectory() {
  return [];
}

export async function resolveRecipients() {
  return { totalCount: 0, resolvedCount: 0, recipients: [] };
}
