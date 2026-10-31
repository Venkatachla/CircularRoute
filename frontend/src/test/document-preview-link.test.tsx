import { renderToString } from "react-dom/server";
import { describe, expect, it } from "vitest";
import DocumentPreview from "@/components/DocumentPreview";
import { formatCircularData } from "@/services/circularService";
import { saveCircularToSession, getCircularFromSession } from "@/services/sessionService";

function render(ui: React.ReactElement) {
  const container = document.createElement("div");
  container.innerHTML = renderToString(ui);
  document.body.appendChild(container);
  return {
    container,
    getByText: (text: string) => {
      const el = Array.from(container.querySelectorAll("*")).find((node) => node.textContent?.includes(text));
      if (!el) throw new Error(`Text "${text}" not found`);
      return el;
    },
    getByRole: (role: string, options?: { name?: RegExp }) => {
      if (role === "link") {
        const links = Array.from(container.querySelectorAll("a"));
        if (options?.name) {
          const matched = links.find((l) => options.name!.test(l.getAttribute("aria-label") || l.textContent || ""));
          if (!matched) throw new Error(`Link with name "${options.name}" not found`);
          return matched;
        }
        if (links.length > 0) return links[0];
      }
      throw new Error(`Role "${role}" not found`);
    },
  };
}

describe("DocumentPreview Link Component", () => {
  it("renders a compact clickable link instead of an embedded preview or iframe", () => {
    const mockCircular = {
      id: "CIR-20261019-8652E8",
      filename: "circular2.jpeg",
      documentUrl: "http://localhost:8000/api/v1/circular/CIR-20261019-8652E8/file",
    };

    const screen = render(<DocumentPreview circular={mockCircular} />);
    const container = screen.container;

    // Must NOT contain an iframe or embedded document element
    expect(container.querySelector("iframe")).toBeNull();
    expect(container.querySelector("embed")).toBeNull();
    expect(container.querySelector("object")).toBeNull();

    // Must display original filename
    expect(screen.getByText("Original circular:")).toBeDefined();
    expect(screen.getByText("circular2.jpeg")).toBeDefined();

    // Must render clickable link targeting actual backend document URL
    const link = screen.getByRole("link", { name: /open original circular circular2\.jpeg in new tab/i });
    expect(link).toBeDefined();
    expect(link.getAttribute("href")).toBe("http://localhost:8000/api/v1/circular/CIR-20261019-8652E8/file");
    expect(link.getAttribute("target")).toBe("_blank");
    expect(link.getAttribute("rel")).toBe("noopener noreferrer");
    expect(link.textContent).toContain("View circular");
  });

  it("renders a clear unavailable state when document URL is missing", () => {
    const mockCircular = {
      id: "CIR-EMPTY",
      filename: "empty.pdf",
      documentUrl: null,
    };

    const screen = render(<DocumentPreview circular={mockCircular} />);
    const container = screen.container;

    expect(container.querySelector("iframe")).toBeNull();
    expect(container.querySelector("a")).toBeNull();
    expect(screen.getByText("Original circular document unavailable")).toBeDefined();
  });

  it("preserves documentUrl and extracted recipients across session persistence", () => {
    sessionStorage.clear();
    const rawData = {
      document_id: "CIR-TEST-001",
      filename: "circular2.jpeg",
      copy_to_found: true,
      copy_to_pages: [1],
      recipients: [
        { raw_text: "The Vice Principals", text: "The Vice Principals", type: "printed", confidence: 0.98, source_page: 1 },
        { raw_text: "The Registrar (Academic)", text: "The Registrar (Academic)", type: "printed", confidence: 0.97, source_page: 1 },
        { raw_text: "The Chief Proctor", text: "The Chief Proctor", type: "printed", confidence: 0.99, source_page: 1 },
        { raw_text: "The IT Coordinator", text: "The IT Coordinator", type: "printed", confidence: 0.96, source_page: 1 },
        { raw_text: "All HODs", text: "All HODs", type: "printed", confidence: 0.95, source_page: 1 },
        { raw_text: "file, students", text: "file, students", type: "handwritten", confidence: 0.85, source_page: 1 }
      ],
      handwritten_text: [
        { text: "file, students", confidence: 0.85, associated_with: "copy_to", source_page: 1 }
      ]
    };

    const formatted = formatCircularData(rawData);
    expect(formatted.documentUrl).toContain("/circular/CIR-TEST-001/file");
    expect(formatted.recipients).toHaveLength(6);

    saveCircularToSession("CIR-TEST-001", formatted);
    const restored = getCircularFromSession("CIR-TEST-001");

    expect(restored).not.toBeNull();
    expect(restored?.filename).toBe("circular2.jpeg");
    expect(restored?.documentUrl).toBe(formatted.documentUrl);
    expect(restored?.recipients).toHaveLength(6);
    expect(restored?.recipients.map((r: any) => r.text)).toEqual([
      "The Vice Principals",
      "The Registrar (Academic)",
      "The Chief Proctor",
      "The IT Coordinator",
      "All HODs",
      "file, students"
    ]);
  });
});
