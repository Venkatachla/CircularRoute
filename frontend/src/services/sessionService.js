const SESSION_PREFIX = "circularroute_session_";
const SESSION_INDEX_KEY = "circularroute_session_index";

function getStorage() {
  if (typeof window !== "undefined" && window.sessionStorage) {
    return window.sessionStorage;
  }
  if (typeof sessionStorage !== "undefined") {
    return sessionStorage;
  }
  return null;
}

/**
 * Reads list of stored circular document IDs in current browser tab session.
 */
export function getSessionCircularIds() {
  const storage = getStorage();
  if (!storage) return [];
  try {
    const raw = storage.getItem(SESSION_INDEX_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (err) {
    console.warn("Failed to read session circular index", err);
    try {
      storage.removeItem(SESSION_INDEX_KEY);
    } catch (_) {}
    return [];
  }
}

/**
 * Adds a document ID to the session index list.
 */
function recordSessionId(documentId) {
  if (!documentId) return;
  const storage = getStorage();
  if (!storage) return;
  try {
    const ids = getSessionCircularIds().filter((id) => id !== documentId);
    ids.unshift(documentId);
    storage.setItem(SESSION_INDEX_KEY, JSON.stringify(ids.slice(0, 50)));
  } catch (_) {}
}

/**
 * Saves or updates circular state in browser sessionStorage for current tab.
 */
export function saveCircularToSession(documentId, circularData) {
  if (!documentId || !circularData) return;
  const storage = getStorage();
  if (!storage) return;
  try {
    const payload = {
      id: circularData.id || documentId,
      ref: circularData.ref || documentId,
      title: circularData.title || circularData.filename || `Circular ${documentId}`,
      filename: circularData.filename || `Circular ${documentId}`,
      file_type: circularData.file_type || "pdf",
      status: circularData.status || "processed",
      copy_to_found: Boolean(circularData.copy_to_found),
      copy_to_pages: circularData.copy_to_pages || [],
      recipients: Array.isArray(circularData.recipients) ? circularData.recipients : [],
      handwritten_text: Array.isArray(circularData.handwritten_text) ? circularData.handwritten_text : [],
      confidence: circularData.confidence ?? 90,
      fieldConfidence: circularData.fieldConfidence || {},
      authority: circularData.authority || "Issuing Authority / Registrar",
      date: circularData.date || new Date().toISOString(),
      departments: circularData.departments || ["cse", "admin"],
      roles: circularData.roles || [],
      recipientPhrase: circularData.recipientPhrase || "",
      instructions: circularData.instructions || "Extract recipients from Copy to section.",
      deadline: circularData.deadline || "Immediate",
      urgency: circularData.urgency || "High",
      documentUrl: circularData.documentUrl || "",
      lastUpdated: new Date().toISOString(),
    };

    storage.setItem(`${SESSION_PREFIX}${documentId}`, JSON.stringify(payload));
    recordSessionId(documentId);
  } catch (err) {
    console.warn(`Failed to save circular ${documentId} to sessionStorage:`, err);
  }
}

/**
 * Retrieves cached circular state from browser sessionStorage.
 * Returns null if missing or malformed.
 */
export function getCircularFromSession(documentId) {
  if (!documentId) return null;
  const storage = getStorage();
  if (!storage) return null;
  try {
    const raw = storage.getItem(`${SESSION_PREFIX}${documentId}`);
    if (!raw) return null;

    const data = JSON.parse(raw);
    if (!data || typeof data !== "object" || !data.id) {
      storage.removeItem(`${SESSION_PREFIX}${documentId}`);
      return null;
    }
    return data;
  } catch (err) {
    console.warn(`Malformed sessionStorage data for ${documentId}, clearing record:`, err);
    try {
      storage.removeItem(`${SESSION_PREFIX}${documentId}`);
    } catch (_) {}
    return null;
  }
}

/**
 * Updates specific fields of an existing circular in sessionStorage.
 */
export function updateCircularInSession(documentId, patch) {
  if (!documentId || !patch) return null;
  const current = getCircularFromSession(documentId);
  if (!current) return null;

  const updated = {
    ...current,
    ...patch,
    lastUpdated: new Date().toISOString(),
  };

  saveCircularToSession(documentId, updated);
  return updated;
}

/**
 * Removes a circular from sessionStorage and the session index.
 */
export function removeCircularFromSession(documentId) {
  if (!documentId) return;
  const storage = getStorage();
  if (!storage) return;
  try {
    storage.removeItem(`${SESSION_PREFIX}${documentId}`);
    const remaining = getSessionCircularIds().filter((id) => id !== documentId);
    storage.setItem(SESSION_INDEX_KEY, JSON.stringify(remaining));
  } catch (_) {}
}
