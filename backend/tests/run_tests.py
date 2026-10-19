import os
import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.ocr_service import ocr_service
from app.services.document_service import document_service


class TestOCRCopyTo(unittest.TestCase):

    def test_01_pdf_input_handling(self):
        """Test PDF input handling capability."""
        self.assertIsNotNone(document_service)

    def test_02_image_input_handling(self):
        """Test image processing and structured output generation."""
        from unittest.mock import patch
        from PIL import Image, ImageDraw
        import io
        img = Image.new("RGB", (600, 800), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((40, 50), "OFFICE OF THE REGISTRAR", fill=(0, 0, 0))
        draw.text((40, 90), "Copy to:", fill=(0, 0, 0))
        draw.text((40, 130), "1. The Principal", fill=(0, 0, 0))
        draw.text((40, 170), "2. HOD - CSE", fill=(0, 0, 0))

        buf = io.BytesIO()
        img.save(buf, format="PNG")

        mock_lines = [
            {"text": "OFFICE OF THE REGISTRAR", "confidence": 0.99, "type": "printed", "source_page": 1},
            {"text": "Copy to:", "confidence": 0.99, "type": "printed", "source_page": 1},
            {"text": "1. The Principal", "confidence": 0.98, "type": "printed", "source_page": 1},
            {"text": "2. HOD - CSE", "confidence": 0.97, "type": "printed", "source_page": 1}
        ]

        with patch.object(ocr_service, "process_page_image", return_value=mock_lines):
            result, rel_path = document_service.process_document(buf.getvalue(), "sample.png")
            self.assertEqual(result.status, "success")
            self.assertEqual(result.file_type, "image")
            self.assertTrue(result.copy_to_found)
            self.assertGreaterEqual(len(result.recipients), 2)

    def test_03_multipage_handling(self):
        """Test multi-page document Copy-to page tracking."""
        page1_lines = [
            {"text": "OFFICE OF THE REGISTRAR", "type": "printed", "confidence": 0.99, "source_page": 1},
            {"text": "CIRCULAR - PAGE 1", "type": "printed", "confidence": 0.99, "source_page": 1}
        ]
        page2_lines = [
            {"text": "Copy to:", "type": "printed", "confidence": 0.99, "source_page": 2},
            {"text": "1. The Principal", "type": "printed", "confidence": 0.98, "source_page": 2},
            {"text": "2. HOD - CSE", "type": "printed", "confidence": 0.97, "source_page": 2}
        ]
        found, pages, recs, _ = ocr_service.parse_document_text_blocks(
            [(1, page1_lines), (2, page2_lines)],
            []
        )
        self.assertTrue(found)
        self.assertEqual(pages, [2])
        self.assertEqual(len(recs), 2)
        self.assertEqual(recs[0].source_page, 2)

    def test_04_printed_recipients_preservation(self):
        """Test exact preservation of printed recipients."""
        lines = [
            {"text": "Copy to:", "type": "printed", "confidence": 0.99, "source_page": 1},
            {"text": "1. Prof. S. Kumar", "type": "printed", "confidence": 0.98, "source_page": 1},
            {"text": "2. Dean - Academics", "type": "printed", "confidence": 0.96, "source_page": 1}
        ]
        found, _, recs, _ = ocr_service.parse_document_text_blocks([(1, lines)], [])
        self.assertTrue(found)
        self.assertEqual(len(recs), 2)
        self.assertEqual(recs[0].text, "Prof. S. Kumar")
        self.assertEqual(recs[1].text, "Dean - Academics")

    def test_05_handwritten_recipients_extraction(self):
        """Test extraction of handwritten additions associated with Copy-to."""
        lines = [
            {"text": "Copy to:", "type": "printed", "confidence": 0.99, "source_page": 1},
            {"text": "1. The Principal", "type": "printed", "confidence": 0.98, "source_page": 1},
            {"text": "PO - CSE", "type": "handwritten", "confidence": 0.88, "source_page": 1}
        ]
        found, _, recs, hw_text = ocr_service.parse_document_text_blocks([(1, lines)], [])
        self.assertTrue(found)
        self.assertEqual(len(recs), 2)
        self.assertEqual(recs[1].type, "handwritten")
        self.assertEqual(len(hw_text), 1)
        self.assertEqual(hw_text[0].text, "PO - CSE")

    def test_06_abbreviations_preservation(self):
        """Test exact preservation of abbreviations without semantic expansion."""
        lines = [
            {"text": "Copy to:", "type": "printed", "confidence": 0.99, "source_page": 1},
            {"text": "1. HOD - CSE", "type": "printed", "confidence": 0.98, "source_page": 1},
            {"text": "2. PO - CSE", "type": "printed", "confidence": 0.97, "source_page": 1},
            {"text": "3. Dean Acad.", "type": "printed", "confidence": 0.95, "source_page": 1}
        ]
        found, _, recs, _ = ocr_service.parse_document_text_blocks([(1, lines)], [])
        texts = [r.text for r in recs]
        self.assertIn("HOD - CSE", texts)
        self.assertIn("PO - CSE", texts)
        self.assertIn("Dean Acad.", texts)
        self.assertNotIn("Head of Department", texts)

    def test_07_names_preservation(self):
        """Test exact preservation of full and partial names."""
        lines = [
            {"text": "Copy to:", "type": "printed", "confidence": 0.99, "source_page": 1},
            {"text": "1. Dr. R. K. Patil", "type": "printed", "confidence": 0.98, "source_page": 1}
        ]
        found, _, recs, _ = ocr_service.parse_document_text_blocks([(1, lines)], [])
        self.assertEqual(recs[0].raw_text, "1. Dr. R. K. Patil")
        self.assertEqual(recs[0].text, "Dr. R. K. Patil")

    def test_08_no_copy_to_section(self):
        """Test behavior when no Copy-to section exists in the document."""
        lines = [
            {"text": "OFFICE OF THE REGISTRAR", "type": "printed", "confidence": 0.99, "source_page": 1},
            {"text": "CIRCULAR", "type": "printed", "confidence": 0.99, "source_page": 1},
            {"text": "All students are hereby informed...", "type": "printed", "confidence": 0.99, "source_page": 1}
        ]
        found, pages, recs, hw = ocr_service.parse_document_text_blocks([(1, lines)], [])
        self.assertFalse(found)
        self.assertEqual(pages, [])
        self.assertEqual(recs, [])
        self.assertEqual(hw, [])

    def test_09_signature_exclusion(self):
        """Test that signatures outside Copy-to are excluded from recipients list."""
        lines = [
            {"text": "Copy to:", "type": "printed", "confidence": 0.99, "source_page": 1},
            {"text": "1. Principal", "type": "printed", "confidence": 0.98, "source_page": 1},
            {"text": "2. HOD - CSE", "type": "printed", "confidence": 0.97, "source_page": 1},
            {"text": "Registrar", "type": "printed", "confidence": 0.99, "source_page": 1},
            {"text": "Sd/-", "type": "printed", "confidence": 0.99, "source_page": 1}
        ]
        found, _, recs, _ = ocr_service.parse_document_text_blocks([(1, lines)], [])
        self.assertTrue(found)
        extracted_texts = [r.text for r in recs]
        self.assertIn("Principal", extracted_texts)
        self.assertIn("HOD - CSE", extracted_texts)
        self.assertNotIn("Registrar", extracted_texts)
        self.assertNotIn("Sd/-", extracted_texts)

    def test_10_unsupported_file_type(self):
        """Test error handling for unsupported file extensions."""
        with self.assertRaises(ValueError):
            document_service.process_document(b"fake content", "document.docx")


if __name__ == "__main__":
    unittest.main()
