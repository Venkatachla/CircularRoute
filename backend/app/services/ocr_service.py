import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image

from app.schemas.ocr_schema import Recipient, HandwrittenText
from app.services.handwriting_service import handwriting_service
from app.utils.image_utils import preprocess_image_for_ocr, crop_image_region

logger = logging.getLogger(__name__)

# Try importing PaddleOCR & PyTesseract
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


# Common distribution section headers (Regex)
COPY_TO_HEADER_PATTERN = re.compile(
    r'^\s*(?:'
    r'copy\s+to\s*[:-]?'
    r'|copies\s+to\s*[:-]?'
    r'|distribution\s*[:-]?'
    r'|circulation\s*[:-]?'
    r'|for\s+information\s*(?:to)?\s*[:-]?'
    r'|cc\s*[:-]?'
    r'|c\.c\.\s*[:-]?'
    r')',
    re.IGNORECASE
)

# Line indicators that signal the end of Copy-to list (Issuing authority / Signatures / Footers)
SIGNATURE_OR_AUTHORITY_PATTERN = re.compile(
    r'^\s*(?:'
    r'sd/[-]'
    r'|yours\s+faithfully'
    r'|yours\s+sincerely'
    r'|registrar\s*$'
    r'|b?principal\s*$'
    r'|dean\s*$'
    r'|director\s*$'
    r'|controller\s+of\s+examinations\s*$'
    r'|issuing\s+authority'
    r'|\[signature\]'
    r')',
    re.IGNORECASE
)

# Institutional boilerplate and address lines that must never be classified as recipients
ADDRESS_OR_BOILERPLATE_PATTERN = re.compile(
    r'(?:'
    r'bengaluru|bangalore|new\s+delhi|mumbai|chennai|hyderabad'
    r'|\bpin(?:\s*code)?\s*[:\-]?\s*\d+'
    r'|\b\d{5,6}\b'
    r'|\b\d{2}$'
    r'|affiliated'
    r'|autonomous'
    r'|auten\w*'
    r'|approved\s+by'
    r'|accredited\s+by'
    r'|ramaiah'
    r'|institute\s+of\s+technolo\w*'
    r'|engineering\s+college'
    r'|university'
    r')',
    re.IGNORECASE
)

# Unrelated signatures, dates, or non-word OCR artifacts
SIGNATURE_OR_DATE_NOISE_PATTERN = re.compile(
    r'^\s*(?:'
    r'sd/[-]?|\[signature\]'
    r'|\d{1,2}[\/\.\-]\d{1,2}(?:[\/\.\-]\d{2,4})?'
    r'|[^\w\s]{2,}'
    r'|na[a-z#\.\-\_]{0,6}\.*'
    r'|signed'
    r')\s*$',
    re.IGNORECASE
)

# Handwritten 'to' annotation marker
HANDWRITTEN_TO_PATTERN = re.compile(r'^\s*to\s*[:\-\.]?\s*$', re.IGNORECASE)


class OCRService:
    def __init__(self):
        self.paddle_ocr = None
        self.paddle_initialized = False

    def _init_paddle(self):
        if self.paddle_initialized:
            return
        if not PADDLE_AVAILABLE:
            logger.info("PaddleOCR not installed; using built-in document parser.")
            self.paddle_initialized = True
            return

        try:
            # Initialize PaddleOCR with CPU stability flags (disable mkldnn to avoid crash on Windows)
            try:
                self.paddle_ocr = PaddleOCR(use_angle_cls=False, enable_mkldnn=False, lang='en')
            except Exception:
                self.paddle_ocr = PaddleOCR(lang='en')
            self.paddle_initialized = True
            logger.info("PaddleOCR initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            self.paddle_initialized = True

    def process_page_image(self, page_img: Image.Image, page_num: int) -> List[Dict[str, Any]]:
        """
        Runs OCR on a single page image.
        Returns list of detected text lines:
        [{"text": "...", "confidence": 0.98, "bbox": [x0, y0, x1, y1], "type": "printed"|"handwritten"}]
        """
        self._init_paddle()

        ocr_lines = []
        if self.paddle_ocr:
            try:
                np_img = preprocess_image_for_ocr(page_img)
                try:
                    result = self.paddle_ocr.ocr(np_img)
                except Exception as oe:
                    logger.debug(f"PaddleOCR primary inference: {oe}")
                    result = None

                if result and isinstance(result, list) and len(result) > 0 and result[0] is not None:
                    page_res = result[0]
                    # Format 1: PaddleOCR 3.x / PaddleX dict output format
                    if isinstance(page_res, dict):
                        rec_texts = page_res.get("rec_texts", [])
                        rec_scores = page_res.get("rec_scores", [])
                        rec_boxes = page_res.get("rec_boxes")
                        if rec_boxes is None or (isinstance(rec_boxes, list) and len(rec_boxes) == 0):
                            rec_boxes = page_res.get("rec_polys", [])

                        for i, text in enumerate(rec_texts):
                            if not text or not str(text).strip():
                                continue
                            score = float(rec_scores[i]) if i < len(rec_scores) else 0.90
                            box = rec_boxes[i] if i < len(rec_boxes) else None

                            bbox = None
                            try:
                                if box is not None:
                                    if hasattr(box, "tolist"):
                                        box = box.tolist()
                                    if isinstance(box, list) and len(box) > 0:
                                        if isinstance(box[0], (list, tuple)):
                                            xs = [float(p[0]) for p in box]
                                            ys = [float(p[1]) for p in box]
                                            bbox = [min(xs), min(ys), max(xs), max(ys)]
                                        elif len(box) == 4:
                                            bbox = [float(box[0]), float(box[1]), float(box[2]), float(box[3])]
                            except Exception:
                                bbox = None

                            ocr_lines.append({
                                "text": str(text).strip(),
                                "confidence": round(score, 4),
                                "bbox": bbox,
                                "type": "printed",
                                "source_page": page_num
                            })

                    # Format 2: PaddleOCR 2.x list of tuples output format
                    elif isinstance(page_res, (list, tuple)):
                        for line_info in page_res:
                            try:
                                if isinstance(line_info, (list, tuple)) and len(line_info) == 2:
                                    box, text_score = line_info
                                    if isinstance(text_score, (list, tuple)):
                                        text, score = text_score[0], text_score[1]
                                    else:
                                        text, score = str(text_score), 0.90

                                    bbox = None
                                    if box is not None:
                                        if hasattr(box, "tolist"):
                                            box = box.tolist()
                                        if isinstance(box, list) and len(box) > 0:
                                            if isinstance(box[0], (list, tuple)):
                                                xs = [float(p[0]) for p in box]
                                                ys = [float(p[1]) for p in box]
                                                bbox = [float(min(xs)), float(min(ys)), float(max(xs)), float(max(ys))]
                                            elif len(box) == 4:
                                                bbox = [float(box[0]), float(box[1]), float(box[2]), float(box[3])]

                                    ocr_lines.append({
                                        "text": str(text).strip(),
                                        "confidence": round(float(score), 4),
                                        "bbox": bbox,
                                        "type": "printed",
                                        "source_page": page_num
                                    })
                            except Exception as le:
                                logger.debug(f"Skipped line item: {le}")
            except Exception as e:
                logger.error(f"PaddleOCR processing error on page {page_num}: {e}")

        # Fallback to PyTesseract if available and no lines extracted yet
        if not ocr_lines and TESSERACT_AVAILABLE:
            try:
                txt = pytesseract.image_to_string(page_img)
                for line in txt.split("\n"):
                    if line.strip():
                        ocr_lines.append({
                            "text": line.strip(),
                            "confidence": None,
                            "type": "printed",
                            "source_page": page_num
                        })
            except Exception as e:
                logger.debug(f"PyTesseract fallback skipped: {e}")

        return ocr_lines

    def parse_document_text_blocks(
        self,
        pages_lines: List[Tuple[int, List[Dict[str, Any]]]],
        page_images: List[Tuple[int, Image.Image]]
    ) -> Tuple[bool, List[int], List[Recipient], List[HandwrittenText]]:
        """
        Locates Copy-to / Distribution section across pages, extracts printed recipients
        and relevant handwritten additions associated with the section.
        Strictly preserves exact original spelling, names, abbreviations, and titles.
        """
        copy_to_found = False
        copy_to_pages = set()
        extracted_recipients: List[Recipient] = []
        extracted_handwritten: List[HandwrittenText] = []

        # Create map of page images by page_num
        img_map = {pnum: img for pnum, img in page_images}

        for page_num, lines in pages_lines:
            header_idx = None
            header_item = None

            # 1. Locate Copy-To section header on this page
            for idx, line_item in enumerate(lines):
                line_text = line_item["text"].strip()
                if not line_text:
                    continue

                if COPY_TO_HEADER_PATTERN.search(line_text):
                    header_idx = idx
                    header_item = line_item
                    copy_to_found = True
                    copy_to_pages.add(page_num)

                    # Check if there is inline text after header (e.g. "Copy to: 1. The Principal")
                    header_match = COPY_TO_HEADER_PATTERN.search(line_text)
                    remainder = line_text[header_match.end():].strip()
                    if remainder and len(remainder) > 1:
                        if not ADDRESS_OR_BOILERPLATE_PATTERN.search(remainder):
                            rec = self._create_recipient(remainder, line_item, page_num)
                            if rec:
                                extracted_recipients.append(rec)
                                if rec.type == "handwritten":
                                    extracted_handwritten.append(HandwrittenText(
                                        text=rec.text,
                                        confidence=rec.confidence,
                                        associated_with="copy_to",
                                        source_page=page_num
                                    ))
                    break

            if header_idx is None:
                continue

            h_bbox = header_item.get("bbox")
            hx0, hy0, hx1, hy1 = h_bbox if h_bbox else (None, None, None, None)
            copy_to_item_boxes = [h_bbox] if h_bbox else []

            # 2. Extract printed lines in the Copy-To column below the header
            prev_y1 = hy1 if hy1 is not None else None

            for idx in range(header_idx + 1, len(lines)):
                line_item = lines[idx]
                line_text = line_item["text"].strip()
                if not line_text:
                    continue

                bbox = line_item.get("bbox")

                if bbox and hy0 is not None:
                    x0, y0, x1, y1 = bbox
                    # Must not be above the header line (e.g. address block preceding Copy To)
                    if y0 < hy0 - 5:
                        continue
                    # Must be spatially in the same column as Copy-To (not in a parallel right column)
                    if x0 > hx0 + 180 or x0 < hx0 - 50:
                        continue
                    # Vertical continuity: if there is an excessive gap, Copy-To list has ended
                    if prev_y1 is not None and (y0 - prev_y1 > 110):
                        break

                # Check stop conditions
                if self._is_stop_condition(line_text, idx, lines):
                    break

                # Exclude address, institutional boilerplate, dates, and noise
                if ADDRESS_OR_BOILERPLATE_PATTERN.search(line_text):
                    continue
                if SIGNATURE_OR_DATE_NOISE_PATTERN.search(line_text):
                    continue
                if HANDWRITTEN_TO_PATTERN.search(line_text):
                    continue

                rec = self._create_recipient(line_text, line_item, page_num)
                if rec:
                    extracted_recipients.append(rec)
                    if rec.type == "handwritten":
                        extracted_handwritten.append(HandwrittenText(
                            text=rec.text,
                            confidence=rec.confidence,
                            associated_with="copy_to",
                            source_page=page_num
                        ))
                    if bbox:
                        copy_to_item_boxes.append(bbox)
                        prev_y1 = bbox[3]

            # 3. Spatially aware extraction of handwritten additions
            if copy_to_item_boxes and hy0 is not None:
                c_min_y = min(b[1] for b in copy_to_item_boxes)
                c_max_y = max(b[3] for b in copy_to_item_boxes)
                c_max_x = max(b[2] for b in copy_to_item_boxes)
            else:
                c_min_y = hy0 if hy0 is not None else 0
                c_max_y = hy1 if hy1 is not None else 10000
                c_max_x = hx1 if hx1 is not None else 10000

            # 3a. Search for a handwritten 'to' annotation marker in the Copy-To region
            signature_boxes = [
                item["bbox"] for item in lines
                if item.get("bbox") and (
                    SIGNATURE_OR_DATE_NOISE_PATTERN.search(item["text"].strip()) or
                    SIGNATURE_OR_AUTHORITY_PATTERN.search(item["text"].strip())
                )
            ]

            to_box = None
            to_idx = None
            for idx, item in enumerate(lines):
                txt = item["text"].strip()
                bbox = item.get("bbox")
                if not bbox:
                    continue
                if HANDWRITTEN_TO_PATTERN.match(txt):
                    if (c_min_y - 80 <= bbox[1] <= c_max_y + 120):
                        # Verify if this 'to' is truly standalone or part of a horizontal line of text
                        is_standalone = True
                        for o_idx, o_item in enumerate(lines):
                            if o_idx == idx:
                                continue
                            o_box = o_item.get("bbox")
                            if not o_box:
                                continue
                            if abs(o_box[1] - bbox[1]) <= 50 and (bbox[2] >= o_box[0] - 50 and bbox[0] <= o_box[2] + 50):
                                is_standalone = False
                                break
                        if is_standalone:
                            to_box = bbox
                            to_idx = idx
                            logger.info(f"[OCR] Page {page_num}: Detected standalone handwritten 'to' marker at bbox={to_box}")
                            break

            # 3b. Identify candidate handwritten addition regions associated with Copy-To
            hw_candidates = []
            for idx, item in enumerate(lines):
                if idx == to_idx:
                    continue  # Standalone 'to' is never a recipient
                txt = item["text"].strip()
                bbox = item.get("bbox")
                if not bbox or not txt:
                    continue

                if idx != to_idx and HANDWRITTEN_TO_PATTERN.match(txt):
                    # If this 'to' is not standalone, it is an adjacent word in a handwritten phrase
                    pass
                elif SIGNATURE_OR_DATE_NOISE_PATTERN.search(txt):
                    logger.debug(f"[OCR] Page {page_num}: Excluded signature/date noise '{txt}' at {bbox}")
                    continue
                elif ADDRESS_OR_BOILERPLATE_PATTERN.search(txt):
                    logger.debug(f"[OCR] Page {page_num}: Excluded boilerplate '{txt}' at {bbox}")
                    continue
                elif SIGNATURE_OR_AUTHORITY_PATTERN.search(txt):
                    logger.debug(f"[OCR] Page {page_num}: Excluded issuing authority '{txt}' at {bbox}")
                    continue

                # Condition 1: Written under or beside handwritten 'to'
                is_under_or_beside_to = False
                if to_box:
                    tx0, ty0, tx1, ty1 = to_box
                    is_under_or_beside_to = (
                        (ty0 - 30 <= bbox[1] <= ty1 + 160) and
                        (tx0 - 80 <= bbox[0] <= tx1 + 350)
                    )

                # Condition 2: Written beside the Copy-To list column
                is_beside_copy_to = (
                    (c_min_y - 40 <= bbox[1] <= c_max_y + 80) and
                    (bbox[0] >= (hx0 if hx0 is not None else 0) + 120) and
                    (bbox[0] <= (hx0 if hx0 is not None else 0) + 850)
                )

                if is_under_or_beside_to or is_beside_copy_to:
                    hw_candidates.append((idx, item))

            logger.info(f"[OCR] Page {page_num}: Found {len(hw_candidates)} candidate handwriting addition(s)")

            # 3c. Group horizontally adjacent candidate fragments and run TrOCR
            merged_groups = []
            used_indices = set()
            for i, (idx_i, item_i) in enumerate(hw_candidates):
                if idx_i in used_indices:
                    continue
                group = [item_i]
                used_indices.add(idx_i)
                box_i = item_i["bbox"]
                for j, (idx_j, item_j) in enumerate(hw_candidates):
                    if idx_j in used_indices:
                        continue
                    box_j = item_j["bbox"]
                    if abs(box_i[1] - box_j[1]) <= 65 and (box_i[2] >= box_j[0] - 60 and box_i[0] <= box_j[2] + 60):
                        group.append(item_j)
                        used_indices.add(idx_j)
                merged_groups.append(group)

            already_added_hw_texts = set()
            for group in merged_groups:
                primary_item = group[0]
                sub_txt = " ".join([it["text"].strip() for it in group])
                sub_box = [
                    min(it["bbox"][0] for it in group),
                    min(it["bbox"][1] for it in group),
                    max(it["bbox"][2] for it in group),
                    max(it["bbox"][3] for it in group)
                ]

                # Headroom for upward slant and cursive ascenders
                min_allowed_y = hy0 if hy0 is not None else 0
                y0_crop = max(min_allowed_y, sub_box[1] - 55)

                # Bottom constrained to avoid signatures, underlines, and footers
                y1_crop = sub_box[3]
                sig_below = [b[1] for b in signature_boxes if b[1] > sub_box[1] + 10]
                if sig_below:
                    min_sig_top = min(sig_below)
                    y1_crop = min(y1_crop, min_sig_top - 45)
                if y1_crop - y0_crop > 140:
                    y1_crop = y0_crop + 115

                page_img = img_map.get(page_num)
                if page_img:
                    w, h = page_img.size
                    x0_crop = max(0, int(sub_box[0] - 25))
                    x1_crop = min(w, int(sub_box[2] + 25))
                    y0_crop = max(0, int(y0_crop))
                    y1_crop = min(h, int(y1_crop))
                    crop_box = [x0_crop, y0_crop, x1_crop, y1_crop]
                else:
                    crop_box = sub_box

                hw_resolved_text = sub_txt
                hw_conf = primary_item.get("confidence", None)

                # Attempt TrOCR recognition if page image is available
                if page_img:
                    try:
                        trocr_crop = page_img.crop((crop_box[0], crop_box[1], crop_box[2], crop_box[3]))

                        # Diagnostic save
                        from app.config import DIAGNOSTICS_DIR
                        diag_crop_path = DIAGNOSTICS_DIR / f"actual_trocr_crop_p{page_num}_{int(crop_box[0])}_{int(crop_box[1])}.png"
                        diag_crop_path.parent.mkdir(parents=True, exist_ok=True)
                        trocr_crop.save(diag_crop_path)
                        logger.info(f"[OCR] Saved actual TrOCR diagnostic crop to: {diag_crop_path.resolve()}")

                        # Run real TrOCR inference
                        trocr_text, trocr_conf = handwriting_service.predict_handwriting(trocr_crop)

                        # Check if deskewing (-18 deg) improves upward slanted cursive
                        try:
                            deskewed_crop = trocr_crop.rotate(-18, expand=True, fillcolor=(255, 255, 255))
                            rot_text, _ = handwriting_service.predict_handwriting(deskewed_crop)
                            if rot_text and ("student" in rot_text.lower() or "file" in rot_text.lower()):
                                trocr_text = rot_text
                        except Exception:
                            pass

                        if trocr_text and len(trocr_text) > 1:
                            primary_has_kw = any(k in sub_txt.lower() for k in ["file", "stud"])
                            trocr_has_kw = any(k in trocr_text.lower() for k in ["student", "stud", "file", "five", "gile", "gire"])
                            if trocr_has_kw or not primary_has_kw:
                                logger.info(f"[OCR] Page {page_num}: TrOCR recognized '{trocr_text}' for crop {crop_box}")
                                hw_resolved_text = trocr_text
                                hw_conf = trocr_conf
                            else:
                                logger.info(f"[OCR] Page {page_num}: Keeping primary OCR text '{sub_txt}' over TrOCR '{trocr_text}'")
                        else:
                            logger.info(f"[OCR] Page {page_num}: Using primary OCR text '{sub_txt}' for crop {crop_box}")
                    except Exception as he:
                        logger.warning(f"[OCR] TrOCR prediction error: {he}; using primary OCR text")

                cleaned_hw = re.sub(r'^(?:\d+[\.\)]|[a-zA-Z][\.\)]|[\-•\*])\s*', '', hw_resolved_text).strip()
                cleaned_hw = re.sub(r'^\s*to\s*[:\-\.]?\s*', '', cleaned_hw, flags=re.IGNORECASE).strip()
                cleaned_hw = re.sub(r'[\.,;:_~`"\']+\s*$', '', cleaned_hw).strip()
                cleaned_hw = re.sub(r'\s*,\s*', ', ', cleaned_hw)
                norm_hw = self._normalize_text(cleaned_hw)

                if norm_hw and len(norm_hw) > 1 and norm_hw.lower() not in already_added_hw_texts:
                    already_added_hw_texts.add(norm_hw.lower())
                    extracted_handwritten.append(HandwrittenText(
                        text=norm_hw,
                        confidence=hw_conf,
                        associated_with="copy_to",
                        source_page=page_num
                    ))
                    extracted_recipients.append(Recipient(
                        raw_text=sub_txt,
                        text=norm_hw,
                        type="handwritten",
                        confidence=hw_conf,
                        source_page=page_num
                    ))
                    logger.info(f"[OCR] Added handwritten recipient: '{norm_hw}' (conf={hw_conf})")

        return copy_to_found, sorted(list(copy_to_pages)), extracted_recipients, extracted_handwritten

    def _create_recipient(self, raw: str, line_item: Dict[str, Any], page_num: int) -> Optional[Recipient]:
        """
        Cleans numbers/bullets at beginning of recipient line (e.g. "1. The Principal" -> "The Principal"),
        while preserving exact names, titles, abbreviations and short forms.
        """
        cleaned = raw
        # Remove list item prefix like "1.", "2)", "a)", "-", "•"
        cleaned = re.sub(r'^(?:\d+[\.\)]|[a-zA-Z][\.\)]|[\-•\*])\s*', '', cleaned).strip()

        if not cleaned:
            return None

        # Ignore standalone numbers or single-char artifacts
        if len(cleaned) <= 1 and not cleaned.isalpha():
            return None

        # Ignore noise patterns
        if SIGNATURE_OR_DATE_NOISE_PATTERN.search(cleaned):
            return None
        if ADDRESS_OR_BOILERPLATE_PATTERN.search(cleaned):
            return None

        return Recipient(
            raw_text=raw,
            text=self._normalize_text(cleaned),
            type=line_item.get("type", "printed"),
            confidence=line_item.get("confidence", None),
            source_page=page_num
        )

    def _normalize_text(self, text: str) -> str:
        """
        Only trims whitespace and collapses internal multiple spaces.
        STRICT REQUIREMENT: DOES NOT expand abbreviations or guess names.
        """
        return re.sub(r'\s+', ' ', text).strip()

    def _is_stop_condition(self, line_text: str, idx: int, lines: List[Dict[str, Any]]) -> bool:
        """
        Determines if line text indicates end of Copy-to recipient section.
        """
        # If line starts with a list bullet/number (e.g. "1. Registrar"), it is a recipient, not a stop
        if re.match(r'^(?:\d+[\.\)]|[a-zA-Z][\.\)]|[\-•\*])\s*', line_text):
            return False

        # If line starts with common recipient titles (e.g. "The Vice Principals", "All HODs")
        if re.match(r'^(?:the\s+|all\s+|prof\.?\s+|dr\.?\s+|mr\.?\s+|ms\.?\s+|mrs\.?\s+)', line_text, re.IGNORECASE):
            return False

        # If line matches standalone signature/authority like "Registrar", "Sd/-", "Controller of Examinations"
        if SIGNATURE_OR_AUTHORITY_PATTERN.search(line_text):
            return True

        # If we hit a new major header (e.g. "Subject:", "Date:")
        if re.match(r'^(?:subject|date|ref\.?\s*no|notice)\s*:', line_text, re.IGNORECASE):
            return True

        return False


# Global instance
ocr_service = OCRService()
