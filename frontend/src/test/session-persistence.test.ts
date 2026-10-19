import { describe, expect, it, beforeEach } from "vitest";
import {
  saveCircularToSession,
  getCircularFromSession,
  updateCircularInSession,
  getSessionCircularIds,
} from "@/services/sessionService";
import { formatCircularData } from "@/services/circularService";

// In-memory mock storage for Vitest/Bun test environment
class MockStorage {
  private store: Record<string, string> = {};

  getItem(key: string): string | null {
    return this.store[key] ?? null;
  }

  setItem(key: string, value: string): void {
    this.store[key] = String(value);
  }

  removeItem(key: string): void {
    delete this.store[key];
  }

  clear(): void {
    this.store = {};
  }
}

const mockSessionStorage = new MockStorage();
if (typeof globalThis.sessionStorage === "undefined") {
  Object.defineProperty(globalThis, "sessionStorage", {
    value: mockSessionStorage,
    writable: true,
  });
}
if (typeof globalThis.window !== "undefined" && typeof globalThis.window.sessionStorage === "undefined") {
  Object.defineProperty(globalThis.window, "sessionStorage", {
    value: mockSessionStorage,
    writable: true,
  });
}

describe("Session Persistence (sessionStorage)", () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it("saves and restores a processed circular across page navigation in the same session", () => {
    const rawOcrData = {
      document_id: "CIR-20261019-ABC1",
      filename: "circular1.jpeg",
      file_type: "image",
      status: "success",
      copy_to_found: true,
      copy_to_pages: [1],
      recipients: [
        {
          raw_text: "1. The Principal",
          text: "The Principal",
          type: "printed",
          confidence: 0.98,
          source_page: 1,
        },
        {
          raw_text: "PO - CSE",
          text: "PO - CSE",
          type: "handwritten",
          confidence: 0.89,
          source_page: 1,
        },
      ],
      handwritten_text: [
        {
          text: "PO - CSE",
          confidence: 0.89,
          associated_with: "copy_to",
          source_page: 1,
        },
      ],
    };

    const formatted = formatCircularData(rawOcrData);
    saveCircularToSession(rawOcrData.document_id, formatted);

    // Simulate navigation away and returning
    const restored = getCircularFromSession("CIR-20261019-ABC1");
    expect(restored).not.toBeNull();
    expect(restored?.id).toBe("CIR-20261019-ABC1");
    expect(restored?.filename).toBe("circular1.jpeg");
    expect(restored?.copy_to_found).toBe(true);
    expect(restored?.recipients).toHaveLength(2);
    expect(restored?.recipients[0].text).toBe("The Principal");
    expect(restored?.recipients[1].text).toBe("PO - CSE");
    expect(restored?.recipients[1].type).toBe("handwritten");
  });

  it("stores multiple circulars separately without overwriting one another", () => {
    const circular1 = formatCircularData({
      document_id: "CIR-DOC-001",
      filename: "first_circular.pdf",
      copy_to_found: true,
      recipients: [{ raw_text: "1. HOD - CSE", text: "HOD - CSE", type: "printed", source_page: 1 }],
    });

    const circular2 = formatCircularData({
      document_id: "CIR-DOC-002",
      filename: "second_circular.pdf",
      copy_to_found: false,
      recipients: [],
    });

    saveCircularToSession("CIR-DOC-001", circular1);
    saveCircularToSession("CIR-DOC-002", circular2);

    const doc1 = getCircularFromSession("CIR-DOC-001");
    const doc2 = getCircularFromSession("CIR-DOC-002");

    expect(doc1?.filename).toBe("first_circular.pdf");
    expect(doc1?.recipients).toHaveLength(1);
    expect(doc1?.recipients[0].text).toBe("HOD - CSE");

    expect(doc2?.filename).toBe("second_circular.pdf");
    expect(doc2?.copy_to_found).toBe(false);
    expect(doc2?.recipients).toHaveLength(0);

    const sessionIds = getSessionCircularIds();
    expect(sessionIds).toContain("CIR-DOC-001");
    expect(sessionIds).toContain("CIR-DOC-002");
  });

  it("updates cached circular data when fields are modified", () => {
    const circular = formatCircularData({
      document_id: "CIR-DOC-003",
      filename: "meeting.pdf",
      copy_to_found: true,
      recipients: [{ raw_text: "Dean", text: "Dean", type: "printed", source_page: 1 }],
    });
    saveCircularToSession("CIR-DOC-003", circular);

    updateCircularInSession("CIR-DOC-003", {
      instructions: "Updated instructions for immediate faculty compliance.",
    });

    const restored = getCircularFromSession("CIR-DOC-003");
    expect(restored?.instructions).toBe("Updated instructions for immediate faculty compliance.");
    expect(restored?.recipients).toHaveLength(1);
  });

  it("handles missing or malformed session data gracefully without throwing", () => {
    // Missing key
    expect(getCircularFromSession("NON-EXISTENT-ID")).toBeNull();

    // Malformed JSON corrupted in sessionStorage
    sessionStorage.setItem("circularroute_session_CORRUPT", "{ not valid json ... ");
    const corruptResult = getCircularFromSession("CORRUPT");
    expect(corruptResult).toBeNull();

    // Invalid object structure
    sessionStorage.setItem("circularroute_session_INVALID", JSON.stringify({ wrong: 123 }));
    const invalidResult = getCircularFromSession("INVALID");
    expect(invalidResult).toBeNull();
  });

  it("handles preview URL gracefully for document rendering", () => {
    const circular = formatCircularData({
      document_id: "CIR-DOC-004",
      filename: "circular4.pdf",
    });
    expect(circular.documentUrl).toContain("/circular/CIR-DOC-004/file");
  });
});
