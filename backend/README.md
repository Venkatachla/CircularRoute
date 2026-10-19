# CircularRoute — Backend OCR & Copy-to Extraction Service

FastAPI-based backend service for extracting "Copy to" / recipient distribution sections from circular PDFs and images.

---

## 1. Overview & Core Philosophy

The backend's single responsibility is:
> **Accept a circular (PDF or image) → Locate "Copy to" / distribution section → Extract printed + relevant handwritten recipients exactly as written → Return structured JSON file in `backend/outputs/`.**

### **Design Principle: READ → PRESERVE → STRUCTURE**
- **Preserves exact original strings**: Names (e.g. `Dr. R. K. Patil`), designations (`HOD - CSE`), abbreviations (`PO - CSE`, `Dean Acad.`), and short forms.
- **NO semantic matching/resolution**: Does NOT expand abbreviations, lookup employee databases, or infer email addresses.

---

## 2. Requirements & Environment Setup

### **Prerequisites**
- Python 3.10+ (Recommended: Python 3.11 or Python 3.12/3.14)
- Virtual Environment (`venv` or `conda`)

### **Setup Steps**

1. Navigate to the `backend` folder:
   ```bash
   cd CircularRoute/backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. *(Optional)* Install PaddlePaddle CPU/GPU support for PP-StructureV3 / PaddleOCR:
   ```bash
   # CPU version
   pip install paddlepaddle -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
   ```

---

## 3. Running the Backend

Start the API server with Uvicorn:

```bash
uvicorn main:app --reload --port 8000
```

The server will be available at:
- **API Base URL**: `http://127.0.0.1:8000`
- **Swagger Documentation**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## 4. API Endpoints

### 1. Health Check
- **`GET /api/health`**
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "CircularRoute Backend"
  }
  ```

### 2. Process Circular
- **`POST /api/circular/process`**
- **Form Data**: `file` (`.pdf`, `.jpg`, `.jpeg`, `.png`, `.webp`)
- **Behavior**:
  1. Validates file format.
  2. Saves raw file to `backend/uploads/`.
  3. Locates Copy-to / distribution list section across pages.
  4. Extracts printed recipients and handwritten annotations.
  5. Saves output JSON to `backend/outputs/<document_id>.json`.
  6. Returns structured response.

### 3. Get Extracted Data
- **`GET /api/circular/{document_id}`**
- Returns the JSON content for the specified document ID.

### 4. Download JSON Output
- **`GET /api/circular/{document_id}/json`**
- Downloads the physical JSON file from `backend/outputs/<document_id>.json`.

---

## 5. Output JSON Schema

```json
{
  "document_id": "CIR-20261007-001",
  "filename": "circular.pdf",
  "file_type": "pdf",
  "status": "success",
  "copy_to_found": true,
  "copy_to_pages": [2],
  "recipients": [
    {
      "raw_text": "The Principal",
      "text": "The Principal",
      "type": "printed",
      "confidence": 0.98,
      "source_page": 2
    },
    {
      "raw_text": "HOD - CSE",
      "text": "HOD - CSE",
      "type": "printed",
      "confidence": 0.96,
      "source_page": 2
    },
    {
      "raw_text": "PO - CSE",
      "text": "PO - CSE",
      "type": "handwritten",
      "confidence": 0.88,
      "source_page": 2
    }
  ],
  "handwritten_text": [
    {
      "text": "PO - CSE",
      "confidence": 0.88,
      "associated_with": "copy_to",
      "source_page": 2
    }
  ]
}
```

---

## 6. Testing

Run backend tests using `pytest`:

```bash
pytest tests/
```

---

## 7. Troubleshooting

- **Unsupported File Type**: Ensure the uploaded file has one of the following extensions: `.pdf`, `.jpg`, `.jpeg`, `.png`, `.webp`.
- **CORS Errors**: The backend allows `http://localhost:5173`. Check `.env` if using a custom port.
