import { request } from "./apiClient";

export async function getDistribution() {
  return request("/distribution");
}

export async function sendCircularMail(documentId, options = {}) {
  return request(`/circular/${encodeURIComponent(documentId)}/send-mail`, {
    method: "POST",
    body: JSON.stringify(options),
  });
}

export async function resolveCircularRecipients(documentId, recipientNames = []) {
  return request(`/circular/${encodeURIComponent(documentId)}/resolve-recipients`, {
    method: "POST",
    body: JSON.stringify({ recipient_names: recipientNames }),
  });
}
