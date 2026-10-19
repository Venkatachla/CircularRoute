import io
from typing import List, Tuple
from PIL import Image

try:
    import pymupdf as fitz  # PyMuPDF
except ImportError:
    fitz = None


def extract_pdf_pages_as_images(pdf_bytes: bytes, dpi: int = 200) -> List[Tuple[int, Image.Image]]:
    """
    Converts a PDF file (bytes) into a list of (page_number_1_indexed, PIL.Image) tuples.
    Uses PyMuPDF (fitz) to render pages at specified DPI.
    """
    if fitz is None:
        raise RuntimeError("PyMuPDF (fitz) is not installed.")

    images = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            images.append((page_idx + 1, img))
    finally:
        doc.close()

    return images


def extract_pdf_page_text_blocks(pdf_bytes: bytes) -> List[Tuple[int, List[dict]]]:
    """
    Extracts native text blocks with coordinates directly from PDF vector text (if available).
    Returns list of (page_number_1_indexed, [block_info_dicts]).
    """
    if fitz is None:
        return []

    page_blocks = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            # get text blocks: (x0, y0, x1, y1, text, block_no, block_type)
            blocks = page.get_text("blocks")
            formatted_blocks = []
            for b in blocks:
                if len(b) >= 5 and b[4].strip():
                    formatted_blocks.append({
                        "bbox": [b[0], b[1], b[2], b[3]],
                        "text": b[4],
                        "lines": [line.strip() for line in b[4].split("\n") if line.strip()]
                    })
            page_blocks.append((page_idx + 1, formatted_blocks))
    finally:
        doc.close()

    return page_blocks
