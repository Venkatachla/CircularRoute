import os
import io
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from app.services.ocr_service import ocr_service

client = TestClient(app)


class TestAPIEndpoints(unittest.TestCase):

    def test_health_check(self):
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "CircularRoute Backend")

    def test_process_circular_success(self):
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (600, 800), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((40, 50), "OFFICE OF THE REGISTRAR", fill=(0, 0, 0))
        draw.text((40, 90), "Copy to:", fill=(0, 0, 0))
        draw.text((40, 130), "1. The Principal", fill=(0, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format="PNG")

        mock_lines = [
            {"text": "OFFICE OF THE REGISTRAR", "confidence": 0.99, "type": "printed", "source_page": 1},
            {"text": "Copy to:", "confidence": 0.99, "type": "printed", "source_page": 1},
            {"text": "1. The Principal", "confidence": 0.98, "type": "printed", "source_page": 1}
        ]

        with patch.object(ocr_service, "process_page_image", return_value=mock_lines):
            response = client.post(
                "/api/circular/process",
                files={"file": ("test_circular.png", buf.getvalue(), "image/png")}
            )

            self.assertEqual(response.status_code, 200)
            res_data = response.json()
            self.assertEqual(res_data["status"], "success")
            self.assertIn("document_id", res_data)
            doc_id = res_data["document_id"]
            self.assertTrue(res_data["data"]["copy_to_found"])

            # Test GET /api/circular/{document_id}
            get_res = client.get(f"/api/circular/{doc_id}")
            self.assertEqual(get_res.status_code, 200)
            self.assertEqual(get_res.json()["document_id"], doc_id)

            # Test GET /api/circular/{document_id}/json
            dl_res = client.get(f"/api/circular/{doc_id}/json")
            self.assertEqual(dl_res.status_code, 200)

            # Test GET /api/circular/{document_id}/file for browser preview
            file_res = client.get(f"/api/circular/{doc_id}/file")
            self.assertEqual(file_res.status_code, 200)
            self.assertEqual(file_res.headers["content-type"], "image/png")

    def test_retired_routes_are_not_found(self):
        # Verify /directory and mail dispatch endpoints are retired
        self.assertEqual(client.get("/api/directory").status_code, 404)
        self.assertEqual(client.post("/api/directory/upload").status_code, 404)
        self.assertEqual(client.post("/api/circular/TEST/resolve-recipients").status_code, 404)
        self.assertEqual(client.post("/api/circular/TEST/send-mail").status_code, 404)

    def test_process_circular_unsupported_file(self):
        response = client.post(
            "/api/circular/process",
            files={"file": ("test_doc.docx", b"dummy content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["error_code"], "UNSUPPORTED_FILE_TYPE")


if __name__ == "__main__":
    unittest.main()
