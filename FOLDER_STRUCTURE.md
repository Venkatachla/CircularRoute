# CircularRoute — Complete Folder Structure Documentation

This document provides a comprehensive, verified inventory and explanation of every relevant directory and file in the **CircularRoute — Intelligent Circular Distribution System** repository.

---

## 1. Project Directory Tree

The complete project folder hierarchy (excluding ephemeral caches and virtual environments) is structured as follows:

```text
CircularRoute/
├── README.md
├── FOLDER_STRUCTURE.md
├── ARCHITECTURE.md
├── COMPONENT_REFERENCE.md
├── backend/
│   ├── .env.example
│   ├── .gitignore
│   ├── README.md
│   ├── main.py
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── circular_routes.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── distribution_schema.py
│   │   │   ├── ocr_schema.py
│   │   │   └── recipient_schema.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── distribution_service.py
│   │   │   ├── document_service.py
│   │   │   ├── email_service.py
│   │   │   ├── handwriting_service.py
│   │   │   ├── json_service.py
│   │   │   ├── ocr_service.py
│   │   │   └── recipient_service.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── image_utils.py
│   │       └── pdf_utils.py
│   ├── backend/
│   │   └── diagnostics/
│   │       ├── actual_trocr_crop_p1_378_1215.png
│   │       └── actual_trocr_crop_p1_595_1338.png
│   ├── data/
│   │   ├── CircularRoute_Data.xlsx
│   │   ├── directory.json
│   │   └── distribution.json
│   ├── diagnostics/
│   │   ├── actual_crop_pipeline.png
│   │   ├── actual_trocr_crop_p1_375_500.png
│   │   ├── actual_trocr_crop_p1_378_1215.png
│   │   ├── actual_trocr_crop_p1_595_1338.png
│   │   ├── crop_broad_handwriting.png
│   │   ├── crop_doc1_line42.png
│   │   ├── crop_perfect_rotated.png
│   │   ├── experiments/
│   │   │   ├── circ1_deskew_35_60.png
│   │   │   ├── circ1_full_rot_-18deg.png
│   │   │   └── ...
│   │   └── ...
│   ├── outputs/
│   │   ├── .gitkeep
│   │   ├── CIR-20261007-134010.json
│   │   ├── CIR-20261019-1A1084.json
│   │   └── ...
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── run_tests.py
│   │   ├── test_api_endpoints.py
│   │   ├── test_ocr_copy_to.py
│   │   └── test_recipient_email_distribution.py
│   └── uploads/
│       ├── .gitkeep
│       ├── CIR-20261007-134010.jpeg
│       ├── CIR-20261019-1A1084.jpeg
│       └── ...
├── data/
│   ├── directory.json
│   └── distribution.json
├── frontend/
│   ├── .gitignore
│   ├── .prettierignore
│   ├── .prettierrc
│   ├── AGENTS.md
│   ├── README.md
│   ├── bun.lock
│   ├── bunfig.toml
│   ├── components.json
│   ├── eslint.config.js
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── vitest.config.ts
│   ├── public/
│   │   └── robots.txt
│   └── src/
│       ├── routeTree.gen.ts
│       ├── router.tsx
│       ├── server.ts
│       ├── start.ts
│       ├── styles.css
│       ├── components/
│       │   ├── ApprovalCard.jsx
│       │   ├── CircularTable.jsx
│       │   ├── ConfidenceScore.jsx
│       │   ├── DecisionFlow.jsx
│       │   ├── DocumentPreview.jsx
│       │   ├── Drawer.jsx
│       │   ├── ExtractionPanel.jsx
│       │   ├── Logo.jsx
│       │   ├── NotificationCenter.jsx
│       │   ├── PageHeader.jsx
│       │   ├── ProcessingPipeline.jsx
│       │   ├── RecipientResolution.jsx
│       │   ├── SearchCommand.jsx
│       │   ├── StatCard.jsx
│       │   ├── States.jsx
│       │   ├── StatusBadge.jsx
│       │   ├── UploadDropzone.jsx
│       │   └── ui/
│       │       ├── accordion.tsx
│       │       ├── alert.tsx
│       │       ├── alert-dialog.tsx
│       │       ├── aspect-ratio.tsx
│       │       ├── avatar.tsx
│       │       ├── badge.tsx
│       │       ├── breadcrumb.tsx
│       │       ├── button.tsx
│       │       ├── calendar.tsx
│       │       ├── card.tsx
│       │       ├── carousel.tsx
│       │       ├── chart.tsx
│       │       ├── checkbox.tsx
│       │       ├── collapsible.tsx
│       │       ├── command.tsx
│       │       ├── context-menu.tsx
│       │       ├── dialog.tsx
│       │       ├── drawer.tsx
│       │       ├── dropdown-menu.tsx
│       │       ├── form.tsx
│       │       ├── hover-card.tsx
│       │       ├── input.tsx
│       │       ├── input-otp.tsx
│       │       ├── label.tsx
│       │       ├── menubar.tsx
│       │       ├── navigation-menu.tsx
│       │       ├── pagination.tsx
│       │       ├── popover.tsx
│       │       ├── progress.tsx
│       │       ├── radio-group.tsx
│       │       ├── resizable.tsx
│       │       ├── scroll-area.tsx
│       │       ├── select.tsx
│       │       ├── separator.tsx
│       │       ├── sheet.tsx
│       │       ├── sidebar.tsx
│       │       ├── skeleton.tsx
│       │       ├── slider.tsx
│       │       ├── sonner.tsx
│       │       ├── switch.tsx
│       │       ├── table.tsx
│       │       ├── tabs.tsx
│       │       ├── textarea.tsx
│       │       ├── toggle.tsx
│       │       ├── toggle-group.tsx
│       │       └── tooltip.tsx
│       ├── hooks/
│       │   └── use-mobile.tsx
│       ├── layouts/
│       │   └── AppShell.jsx
│       ├── lib/
│       │   ├── error-capture.ts
│       │   ├── error-page.ts
│       │   ├── lovable-error-reporting.ts
│       │   └── utils.ts
│       ├── routes/
│       │   ├── README.md
│       │   ├── __root.tsx
│       │   ├── _shell.jsx
│       │   ├── _shell.approvals.jsx
│       │   ├── _shell.audit.jsx
│       │   ├── _shell.circulars.$id.jsx
│       │   ├── _shell.circulars.index.jsx
│       │   ├── _shell.distribution.jsx
│       │   ├── _shell.index.jsx
│       │   ├── _shell.recipients.jsx
│       │   ├── _shell.settings.jsx
│       │   ├── _shell.upload.jsx
│       │   └── login.jsx
│       ├── services/
│       │   ├── apiClient.js
│       │   ├── auditService.js
│       │   ├── circularService.js
│       │   ├── distributionService.js
│       │   ├── recipientService.js
│       │   └── sessionService.js
│       ├── test/
│       │   ├── app-routing.test.tsx
│       │   ├── document-preview-link.test.tsx
│       │   ├── session-persistence.test.ts
│       │   └── setup.ts
│       └── utils/
│           └── format.js
├── outputs/
│   ├── CIR-20261019-1A1084.json
│   ├── CIR-20261019-52B3FE.json
│   └── ...
└── uploads/
    ├── CIR-20261019-1A1084.jpeg
    ├── CIR-20261019-52B3FE.jpeg
    └── ...
```

---

## 2. Generated and Excluded Directories Summary

The following directories exist within the project workspace but are generated build artifacts, package dependencies, or virtual runtime environments. They are omitted from individual line-by-line file inventories to prevent clutter:

1. **`backend/venv/`**: Python 3.11 virtual environment containing installed backend packages (`fastapi`, `uvicorn`, `paddleocr`, `paddlepaddle`, `transformers`, `torch`, `pymupdf`, `pillow`, `opencv-python`, `pytest`, `httpx`).
2. **`frontend/node_modules/`**: Node.js / Bun installed packages for the frontend (`react`, `@tanstack/react-start`, `@tanstack/react-router`, `@radix-ui/*`, `tailwindcss`, `vite`, `vitest`).
3. **`frontend/.output/`**: Build bundle output generated by Vite/Nitro for deployment.
4. **`frontend/.tanstack/`**: Temporary cache directory used by TanStack Start router codegen.
5. **`frontend/.wrangler/`**: Local cache directory generated when preparing Cloudflare / Nitro deployments.
6. **`.pytest_cache/`**: Cache directory generated by the pytest test runner.
7. **`.git/`**: Git source control database tracking commits and revisions.

---

## 3. Root Level Files and Directories

### `README.md`
- **Path:** [README.md](file:///c:/Users/Asus/Documents/CircularRoute/README.md)
- **Type:** Markdown Documentation
- **Purpose:** Top-level project title marker.
- **Uses and responsibilities:** Serves as the repository header placeholder.
- **Important contents:** `# CircularRoute` header.
- **Dependencies:** None.
- **Used by:** GitHub repository overview.
- **Inputs/Outputs:** N/A.
- **Implementation status:** Implemented (minimal placeholder).

### `data/`
- **Path:** `data/`
- **Type:** Directory (Runtime Data Storage)
- **Purpose:** Root-level storage for directory and distribution JSON data used when operating from root CWD.
- **Uses and responsibilities:** Mirrors or provides data fallback for offline recipient lists and delivery logs.
- **Important contents:** `directory.json`, `distribution.json`.
- **Dependencies:** Filesystem.
- **Used by:** Backend services when configured with `DATA_DIR=data`.
- **Inputs/Outputs:** JSON serialization.
- **Implementation status:** Implemented.

#### `data/directory.json`
- **Path:** [data/directory.json](file:///c:/Users/Asus/Documents/CircularRoute/data/directory.json)
- **Type:** JSON Data File
- **Purpose:** Empty directory list placeholder `[]`.
- **Implementation status:** Implemented.

#### `data/distribution.json`
- **Path:** [data/distribution.json](file:///c:/Users/Asus/Documents/CircularRoute/data/distribution.json)
- **Type:** JSON Data File
- **Purpose:** Contains sample dispatch timeline events and distribution row entries.
- **Implementation status:** Implemented.

### `outputs/` (Legacy)
- **Path:** `outputs/`
- **Type:** Directory (Legacy Storage — Migrated to `backend/outputs/`)
- **Purpose:** Historical directory from earlier root-level executions. All structured outputs have been safely migrated to canonical `backend/outputs/`.
- **Implementation status:** Deprecated / Retained for safety until approved for deletion.

### `uploads/` (Legacy)
- **Path:** `uploads/`
- **Type:** Directory (Legacy Storage — Migrated to `backend/uploads/`)
- **Purpose:** Historical directory from earlier root-level executions. All uploaded documents have been safely migrated to canonical `backend/uploads/`.
- **Implementation status:** Deprecated / Retained for safety until approved for deletion.

---

## 4. Backend Modules and Files

### `backend/`
- **Path:** `backend/`
- **Type:** Directory (Python FastAPI Backend Service)
- **Purpose:** Contains the complete Python backend application responsible for file ingestion, PDF page rendering, PaddleOCR text extraction, Copy-To spatial region parsing, TrOCR handwriting inference, and JSON persistence.

### `backend/.env.example`
- **Path:** [backend/.env.example](file:///c:/Users/Asus/Documents/CircularRoute/backend/.env.example)
- **Type:** Configuration Template
- **Purpose:** Template defining required and optional environment variables.
- **Important contents:** `APP_NAME`, `HOST`, `PORT`, `FRONTEND_URL`, `UPLOAD_DIR`, `OUTPUT_DIR`, `DATA_DIR`, `SMTP_*`.
- **Implementation status:** Implemented.

### `backend/.gitignore`
- **Path:** [backend/.gitignore](file:///c:/Users/Asus/Documents/CircularRoute/backend/.gitignore)
- **Type:** Git Configuration
- **Purpose:** Ignores Python virtual environments (`venv/`), `__pycache__`, environment files (`.env`), test caches, and output directories.
- **Implementation status:** Implemented.

### `backend/README.md`
- **Path:** [backend/README.md](file:///c:/Users/Asus/Documents/CircularRoute/backend/README.md)
- **Type:** Documentation
- **Purpose:** Documents backend design philosophy ("READ -> PRESERVE -> STRUCTURE"), prerequisites, API endpoints, output schema, and execution commands.
- **Implementation status:** Implemented.

### `backend/main.py`
- **Path:** [backend/main.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/main.py)
- **Type:** Python Module (Application Entry Point)
- **Purpose:** Initializes FastAPI application, configures CORS middleware, loads environment variables, registers API routers, and defines root endpoint.
- **Important contents:** `app = FastAPI(...)`, CORS configuration, `app.include_router(circular_router)`, `root()`.
- **Dependencies:** `fastapi`, `uvicorn`, `python-dotenv`, [circular_routes.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/api/circular_routes.py).
- **Used by:** Uvicorn execution command (`uvicorn main:app`).
- **Implementation status:** Implemented.

### `backend/requirements.txt`
- **Path:** [backend/requirements.txt](file:///c:/Users/Asus/Documents/CircularRoute/backend/requirements.txt)
- **Type:** Dependency Manifest
- **Purpose:** Lists pip dependencies with version constraints.
- **Important contents:** `fastapi`, `uvicorn[standard]`, `python-multipart`, `pydantic`, `python-dotenv`, `pymupdf`, `pillow`, `opencv-python`, `paddleocr`, `paddlepaddle`, `transformers`, `torch`, `pytest`, `httpx`, `openpyxl`.
- **Implementation status:** Implemented.

### `backend/app/`
- **Path:** `backend/app/`
- **Type:** Python Package
- **Purpose:** Application source code root containing `api/`, `schemas/`, `services/`, and `utils/`.
- **Implementation status:** Implemented.

### `backend/app/api/circular_routes.py`
- **Path:** [backend/app/api/circular_routes.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/api/circular_routes.py)
- **Type:** Python Module (FastAPI Router)
- **Purpose:** Defines the active HTTP REST endpoints exposed by the service.
- **Important contents:**
  - `GET /api/health`: Health status endpoint.
  - `POST /api/circular/process`: Uploads circular, triggers OCR, and returns extraction payload.
  - `GET /api/circular/{document_id}`: Fetches stored JSON output.
  - `GET /api/circular/{document_id}/json`: Downloads raw physical `.json` file.
  - `GET /api/circular/{document_id}/file`: Serves original circular PDF/image for browser preview.
- **Dependencies:** `fastapi`, [document_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/document_service.py), [json_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/json_service.py), [ocr_schema.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/schemas/ocr_schema.py).
- **Used by:** [main.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/main.py).
- **Implementation status:** Implemented.

### `backend/app/schemas/ocr_schema.py`
- **Path:** [backend/app/schemas/ocr_schema.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/schemas/ocr_schema.py)
- **Type:** Python Module (Pydantic Models)
- **Purpose:** Strict schema definitions for OCR extraction and API responses.
- **Important contents:**
  - `Recipient`: `raw_text`, `text`, `type` ("printed"|"handwritten"), `confidence`, `source_page`.
  - `HandwrittenText`: `text`, `confidence`, `associated_with`, `source_page`.
  - `OCRResult`: `document_id`, `filename`, `file_type`, `status`, `copy_to_found`, `copy_to_pages`, `recipients`, `handwritten_text`.
  - `ProcessResponse`: `status`, `document_id`, `output_file`, `data: OCRResult`.
  - `ErrorResponse`: `status`, `error_code`, `message`.
- **Dependencies:** `pydantic`.
- **Used by:** [document_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/document_service.py), [ocr_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/ocr_service.py), [circular_routes.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/api/circular_routes.py).
- **Implementation status:** Implemented.

### `backend/app/schemas/recipient_schema.py`
- **Path:** [backend/app/schemas/recipient_schema.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/schemas/recipient_schema.py)
- **Type:** Python Module (Pydantic Models)
- **Purpose:** Schemas for directory records and recipient resolution.
- **Important contents:** `DirectoryEntry`, `ResolvedRecipient`, `RecipientResolutionRequest`, `RecipientResolutionResponse`.
- **Dependencies:** `pydantic`.
- **Used by:** [recipient_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/recipient_service.py).
- **Implementation status:** Decoupled / Dormant (endpoints retired from active API routing).

### `backend/app/schemas/distribution_schema.py`
- **Path:** [backend/app/schemas/distribution_schema.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/schemas/distribution_schema.py)
- **Type:** Python Module (Pydantic Models)
- **Purpose:** Schemas for email distribution payloads, timeline events, and delivery status rows.
- **Important contents:** `EmailRecipientPayload`, `SendMailRequest`, `DistributionRow`, `TimelineEvent`, `DistributionResponse`.
- **Dependencies:** `pydantic`.
- **Used by:** [distribution_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/distribution_service.py), [email_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/email_service.py).
- **Implementation status:** Decoupled / Dormant (endpoints retired from active API routing).

### `backend/app/services/document_service.py`
- **Path:** [backend/app/services/document_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/document_service.py)
- **Type:** Python Module (Orchestrator Service)
- **Purpose:** Validates uploaded file types, generates unique Document IDs (`CIR-YYYYMMDD-XXXXXX`), saves files to canonical `backend/uploads/`, extracts pages from PDFs or loads images, coordinates OCR parsing, and saves output JSON files to `backend/outputs/`.
- **Important contents:** `generate_document_id()`, `is_allowed_file()`, `save_upload_file()`, `DocumentService.process_document()`.
- **Dependencies:** [pdf_utils.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/utils/pdf_utils.py), [image_utils.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/utils/image_utils.py), [ocr_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/ocr_service.py), [json_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/json_service.py).
- **Used by:** [circular_routes.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/api/circular_routes.py), test suites.
- **Implementation status:** Implemented.

### `backend/app/services/ocr_service.py`
- **Path:** [backend/app/services/ocr_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/ocr_service.py)
- **Type:** Python Module (OCR Pipeline Engine)
- **Purpose:** The core 600+ line OCR engine. Manages PaddleOCR initialization (supporting both 2.x and 3.x result formats), PyTesseract fallback, regex header detection (`COPY_TO_HEADER_PATTERN`), spatial column filtering, signature/date/boilerplate exclusion, handwritten 'to' anchor detection, dynamic bounding box calculation, diagnostic crop saving, and TrOCR inference invocation with deskew validation.
- **Important contents:** `OCRService.process_page_image()`, `OCRService.parse_document_text_blocks()`, `_create_recipient()`, `_normalize_text()`, `_is_stop_condition()`.
- **Dependencies:** `paddleocr`, `PIL`, `pytesseract` (optional), [handwriting_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/handwriting_service.py), [image_utils.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/utils/image_utils.py).
- **Used by:** [document_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/document_service.py), test suites.
- **Implementation status:** Implemented.

### `backend/app/services/handwriting_service.py`
- **Path:** [backend/app/services/handwriting_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/handwriting_service.py)
- **Type:** Python Module (Transformer Handwriting Model)
- **Purpose:** Manages Microsoft TrOCR (`microsoft/trocr-base-handwritten`). Implements lazy loading, checks local Hugging Face cache for non-blocking offline operation, prepares image tensors, and generates transcribed text for cropped regions.
- **Important contents:** `HandwritingService._initialize_model()`, `is_model_loaded()`, `predict_handwriting(image)`.
- **Dependencies:** `transformers` (`TrOCRProcessor`, `VisionEncoderDecoderModel`), `torch`, `PIL`.
- **Used by:** [ocr_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/ocr_service.py).
- **Implementation status:** Implemented (with graceful fallback if model weights are not cached).

### `backend/app/services/json_service.py`
- **Path:** [backend/app/services/json_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/json_service.py)
- **Type:** Python Module (Persistence Service)
- **Purpose:** Reads and writes physical JSON output files in the target directory (`backend/outputs/<document_id>.json`).
- **Important contents:** `save_output_json(ocr_result)`, `load_output_json(document_id)`.
- **Dependencies:** `json`, `pathlib`, [ocr_schema.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/schemas/ocr_schema.py).
- **Used by:** [document_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/document_service.py), [circular_routes.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/api/circular_routes.py).
- **Implementation status:** Implemented.

### `backend/app/services/recipient_service.py`
- **Path:** [backend/app/services/recipient_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/recipient_service.py)
- **Type:** Python Module (Fuzzy Recipient Directory Matcher)
- **Purpose:** Matches extracted recipient strings against an Excel database (`CircularRoute_Data.xlsx`) or JSON directory using difflib `SequenceMatcher`, title alias normalization, and token containment.
- **Important contents:** `RecipientService.load_directory_from_excel()`, `resolve_recipients()`, `_match_phrase_to_directory()`.
- **Dependencies:** `openpyxl`, `difflib`, `pydantic`.
- **Used by:** Decoupled from public API; tested in legacy test suites.
- **Implementation status:** Decoupled / Standalone service.

### `backend/app/services/distribution_service.py`
- **Path:** [backend/app/services/distribution_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/distribution_service.py)
- **Type:** Python Module (Distribution State Manager)
- **Purpose:** Manages dispatch status rows and timeline events, persisting them to `distribution.json`.
- **Important contents:** `DistributionService.record_distribution()`, `get_distribution()`.
- **Dependencies:** `json`, `datetime`, [email_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/email_service.py).
- **Used by:** Decoupled from public API.
- **Implementation status:** Decoupled / Standalone service.

### `backend/app/services/email_service.py`
- **Path:** [backend/app/services/email_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/email_service.py)
- **Type:** Python Module (SMTP Dispatch Service)
- **Purpose:** Dispatches multipart HTML emails with optional document attachments via live SMTP, or executes simulated dispatches when SMTP is unconfigured.
- **Important contents:** `EmailService.send_circular_emails()`, `_send_single_email()`.
- **Dependencies:** `smtplib`, `email.mime`, `asyncio`.
- **Used by:** [distribution_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/distribution_service.py).
- **Implementation status:** Decoupled / Standalone service.

### `backend/app/utils/image_utils.py`
- **Path:** [backend/app/utils/image_utils.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/utils/image_utils.py)
- **Type:** Python Module (Image Preprocessing Utilities)
- **Purpose:** Converts raw bytes into RGB PIL Images, applies OpenCV CLAHE contrast enhancement for OCR preprocessing, and performs bounding-box cropping with configurable padding.
- **Important contents:** `load_image_from_bytes()`, `preprocess_image_for_ocr()`, `crop_image_region()`.
- **Dependencies:** `PIL`, `cv2` (OpenCV), `numpy`.
- **Used by:** [document_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/document_service.py), [ocr_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/ocr_service.py).
- **Implementation status:** Implemented.

### `backend/app/utils/pdf_utils.py`
- **Path:** [backend/app/utils/pdf_utils.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/utils/pdf_utils.py)
- **Type:** Python Module (PyMuPDF Utilities)
- **Purpose:** Extracts native text blocks with bounding boxes directly from vector PDFs and renders PDF pages to high-resolution (200 DPI) PIL images for optical character recognition.
- **Important contents:** `extract_pdf_pages_as_images()`, `extract_pdf_page_text_blocks()`.
- **Dependencies:** `pymupdf` (`fitz`), `PIL`.
- **Used by:** [document_service.py](file:///c:/Users/Asus/Documents/CircularRoute/backend/app/services/document_service.py).
- **Implementation status:** Implemented.

### `backend/data/`
- **Path:** `backend/data/`
- **Type:** Directory (Directory Databases)
- **Purpose:** Stores the institution directory Excel sheet and cached directory/distribution JSON files.
- **Important contents:**
  - `CircularRoute_Data.xlsx`: Academic faculty and department directory spreadsheet.
  - `directory.json`: 33 cached faculty records parsed from the Excel file with precomputed aliases.
  - `distribution.json`: Sample delivery records and timeline log.
- **Implementation status:** Implemented.

### `backend/diagnostics/`
- **Path:** `backend/diagnostics/`
- **Type:** Directory (Diagnostic Image Crops)
- **Purpose:** Stores visual artifacts generated during TrOCR inference, bounding box deskewing, and OCR threshold experiments.
- **Important contents:** Diagnostic crops such as `actual_trocr_crop_p1_378_1215.png`, `crop_perfect_rotated.png`, `doc1_file_students_textline.png`, and the `experiments/` subfolder containing deskew angles from -15° to -30°.
- **Implementation status:** Implemented (active debug target).

### `backend/tests/`
- **Path:** `backend/tests/`
- **Type:** Directory (Test Suite)
- **Purpose:** Unit and integration tests verifying OCR extraction, file validation, API endpoints, schema contracts, and abbreviation preservation.
- **Important contents:**
  - `run_tests.py`: Standalone unittest runner testing 10 core OCR cases (10/10 passed).
  - `test_api_endpoints.py`: Integration test suite using FastAPI `TestClient` for `/api/health`, `/api/circular/process`, and error cases (4/4 passed).
  - `test_ocr_copy_to.py`: Comprehensive test suite verifying multi-page tracking, printed vs handwritten classification, and noise filtering (16/16 passed).
  - `test_recipient_email_distribution.py`: Verifies strict preservation of abbreviations without semantic expansion and confirms retired endpoints return 404 (4/4 passed).
- **Implementation status:** Implemented (all 24 pytest tests verified passing).

---

## 5. Frontend Architecture and Files

### `frontend/`
- **Path:** `frontend/`
- **Type:** Directory (Modern React 19 / TanStack Start Application)
- **Purpose:** Single-page and server-rendered web application providing the circular upload interface, decision flow, preview canvas, and recipient inspection dashboard.

### `frontend/package.json`
- **Path:** [frontend/package.json](file:///c:/Users/Asus/Documents/CircularRoute/frontend/package.json)
- **Type:** NPM Package Manifest
- **Purpose:** Defines project scripts, dependencies, devDependencies, and package overrides (`rolldown: 1.2.1`).
- **Dependencies:** React 19 (`react`, `react-dom`), `@tanstack/react-start`, `@tanstack/react-router`, `@tanstack/react-query`, Radix UI primitives, Tailwind CSS v4, `motion`, `lucide-react`, `recharts`, `sonner`, `zod`.
- **Implementation status:** Implemented.

### `frontend/vite.config.ts`
- **Path:** [frontend/vite.config.ts](file:///c:/Users/Asus/Documents/CircularRoute/frontend/vite.config.ts)
- **Type:** Vite Configuration
- **Purpose:** Configures `@lovable.dev/vite-tanstack-config` with custom server entry redirection to `src/server.ts` for SSR error handling.
- **Implementation status:** Implemented.

### `frontend/vitest.config.ts`
- **Path:** [frontend/vitest.config.ts](file:///c:/Users/Asus/Documents/CircularRoute/frontend/vitest.config.ts)
- **Type:** Vitest Configuration
- **Purpose:** Configures unit test runner with jsdom environment, global matchers, setup file (`src/test/setup.ts`), and `@` path alias.
- **Implementation status:** Implemented.

### `frontend/tsconfig.json`
- **Path:** [frontend/tsconfig.json](file:///c:/Users/Asus/Documents/CircularRoute/frontend/tsconfig.json)
- **Type:** TypeScript Configuration
- **Purpose:** Declares TypeScript compiler options (target `ES2022`, module `ESNext`, strict type checking, `@/*` path mapping).
- **Implementation status:** Implemented.

### `frontend/eslint.config.js`
- **Path:** [frontend/eslint.config.js](file:///c:/Users/Asus/Documents/CircularRoute/frontend/eslint.config.js)
- **Type:** ESLint Configuration
- **Purpose:** Configures ESLint with TypeScript ESLint, React hooks rules, Prettier integration, and disallows `server-only` Next.js import.
- **Implementation status:** Implemented.

### `frontend/components.json`
- **Path:** [frontend/components.json](file:///c:/Users/Asus/Documents/CircularRoute/frontend/components.json)
- **Type:** shadcn/ui Configuration
- **Purpose:** Declares shadcn UI settings (New York style, Slate base color, Tailwind CSS v4 variables, Lucide icons, `@/components` aliases).
- **Implementation status:** Implemented.

### `frontend/bunfig.toml`
- **Path:** [frontend/bunfig.toml](file:///c:/Users/Asus/Documents/CircularRoute/frontend/bunfig.toml)
- **Type:** Bun Configuration
- **Purpose:** Configures 24-hour supply chain security guard for npm packages.
- **Implementation status:** Implemented.

### `frontend/src/`
- **Path:** `frontend/src/`
- **Type:** Directory (Application Source Code)
- **Purpose:** Holds router, entrypoints, styling, layouts, routes, components, and services.

### `frontend/src/start.ts`
- **Path:** [frontend/src/start.ts](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/start.ts)
- **Type:** TypeScript Module (TanStack Start Initialization)
- **Purpose:** Creates the TanStack Start instance with server error middleware and CSRF protection middleware for server functions.
- **Implementation status:** Implemented.

### `frontend/src/server.ts`
- **Path:** [frontend/src/server.ts](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/server.ts)
- **Type:** TypeScript Module (SSR Server Entry)
- **Purpose:** Serves as the Nitro/Vite SSR server entry. Catches unhandled h3 exceptions and renders clean HTML error fallback pages.
- **Implementation status:** Implemented.

### `frontend/src/router.tsx`
- **Path:** [frontend/src/router.tsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/router.tsx)
- **Type:** TypeScript Module (Router Factory)
- **Purpose:** Initializes TanStack Router with `QueryClient`, scroll restoration, and generated route tree.
- **Implementation status:** Implemented.

### `frontend/src/routeTree.gen.ts`
- **Path:** [frontend/src/routeTree.gen.ts](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/routeTree.gen.ts)
- **Type:** TypeScript Module (Generated Route Tree)
- **Purpose:** Auto-generated file connecting TanStack Router routes.
- **Implementation status:** Implemented (auto-generated).

### `frontend/src/styles.css`
- **Path:** [frontend/src/styles.css](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/styles.css)
- **Type:** CSS Stylesheet
- **Purpose:** Core design system using Tailwind CSS v4 `@theme inline`, OKLCH institutional colors (navy, electric blue, warning amber, success emerald), IBM Plex fonts, and custom utility classes (`card-surface`, `label-caps`, `grid-dots`).
- **Implementation status:** Implemented.

### `frontend/src/layouts/AppShell.jsx`
- **Path:** [frontend/src/layouts/AppShell.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/layouts/AppShell.jsx)
- **Type:** React Layout Component
- **Purpose:** Institutional application shell featuring a responsive navigation sidebar (collapsible on desktop, drawer on mobile), header bar with search shortcut (`Ctrl+K`), notification popover, institutional branding, and user account menu.
- **Implementation status:** Implemented.

### `frontend/src/routes/`
- **Path:** `frontend/src/routes/`
- **Type:** Directory (File-Based Route Definitions)
- **Purpose:** Declares all pages and layouts via TanStack Router conventions.

| Route File | Path Matched | Purpose | Implementation Status |
|---|---|---|---|
| [__root.tsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/routes/__root.tsx) | Root Shell | Global HTML shell, fonts, QueryClientProvider, and Toaster | Implemented |
| [_shell.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/routes/_shell.jsx) | `/_shell` | Wraps authenticated views inside `AppShell` | Implemented |
| [_shell.index.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/routes/_shell.index.jsx) | `/` | Dashboard overview with volume area chart, department bar chart, and recent circulars table | Implemented |
| [_shell.upload.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/routes/_shell.upload.jsx) | `/upload` | Circular upload dropzone and live 3-stage progress pipeline | Implemented |
| [_shell.circulars.index.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/routes/_shell.circulars.index.jsx) | `/circulars` | Library of all processed circulars with search and filter tabs | Implemented |
| [_shell.circulars.$id.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/routes/_shell.circulars.$id.jsx) | `/circulars/:id` | Circular details, confidence scores, original document preview, and extracted recipient cards | Implemented |
| [_shell.recipients.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/routes/_shell.recipients.jsx) | `/recipients` | Recipient directory preview interface | Planned / Placeholder |
| [_shell.distribution.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/routes/_shell.distribution.jsx) | `/distribution` | Delivery timeline and recipient dispatch status table | Implemented (view only) |
| [_shell.approvals.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/routes/_shell.approvals.jsx) | `/approvals` | Human-in-the-loop review cards for low-confidence circulars | Implemented (demo state) |
| [_shell.audit.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/routes/_shell.audit.jsx) | `/audit` | Compliance audit log table with detail drawer | Implemented (demo state) |
| [_shell.settings.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/routes/_shell.settings.jsx) | `/settings` | Distribution threshold slider and notification switches | Implemented |
| [login.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/routes/login.jsx) | `/login` | Branded split-screen sign-in form | Implemented (demo UI) |

### `frontend/src/components/`
- **Path:** `frontend/src/components/`
- **Type:** Directory (Application UI Components)
- **Purpose:** Reusable feature and presentation components.

- [DocumentPreview.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/DocumentPreview.jsx): Embeds link and metadata banner linking to the original uploaded file (`GET /api/circular/{id}/file`).
- [RecipientResolution.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/RecipientResolution.jsx): Displays extracted Copy-To recipients with distinction between printed (`FileText`) and handwritten (`PenTool`) items, confidence scores, and source pages.
- [ExtractionPanel.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/ExtractionPanel.jsx): Displays overall extraction confidence ring, breakdown bars, and editable metadata fields.
- [UploadDropzone.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/UploadDropzone.jsx): Drag-and-drop file upload target supporting PDF, DOCX, PNG, JPG, and JPEG files.
- [CircularTable.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/CircularTable.jsx): Responsive desktop table and mobile card list for circular records.
- [DecisionFlow.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/DecisionFlow.jsx): Animated flow diagram showing confidence scoring and automatic distribution threshold check.
- [ProcessingPipeline.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/ProcessingPipeline.jsx): Vertical animated pipeline showing step-by-step document ingestion progress.
- [ConfidenceScore.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/ConfidenceScore.jsx): Animated circular confidence ring and compact tabular progress bar.
- [ApprovalCard.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/ApprovalCard.jsx): Human review card with quick Approve/Reject actions.
- [StatCard.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/StatCard.jsx): Metric card with animated sparklines and trend indicators.
- [States.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/States.jsx): Empty, Error, and Skeleton loading states.
- [StatusBadge.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/StatusBadge.jsx): Color-coded status badge with pulsing indicator.
- [Logo.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/Logo.jsx): Institutional vector logo representing circular distribution.
- [PageHeader.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/PageHeader.jsx): Standard page header with eyebrow, title, subtitle, and action buttons.
- [SearchCommand.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/SearchCommand.jsx): Accessible `Ctrl+K` command palette dialog.
- [NotificationCenter.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/NotificationCenter.jsx): Header notification bell popover.
- [Drawer.jsx](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/components/Drawer.jsx): Accessible slide-over side drawer for audit log inspection.

### `frontend/src/services/`
- **Path:** `frontend/src/services/`
- **Type:** Directory (API Clients and State Services)
- **Purpose:** Handles backend communication, data formatting, and tab-level session persistence.

- [apiClient.js](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/services/apiClient.js): Generic `fetch` wrapper communicating with `http://localhost:8000/api`.
- [circularService.js](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/services/circularService.js): Uploads circulars (`uploadCircular`), fetches circular details (`getCircular`), lists recent circulars (`listCirculars`), and formats dashboard metrics (`getDashboard`).
- [sessionService.js](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/services/sessionService.js): Implements browser `sessionStorage` caching (`circularroute_session_<id>`), ensuring that navigating back and forth across tabs never loses extracted circular state.
- [recipientService.js](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/services/recipientService.js): Decoupled placeholder for downstream recipient matching services.
- [distributionService.js](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/services/distributionService.js): Service returning distribution timeline and rows.
- [auditService.js](file:///c:/Users/Asus/Documents/CircularRoute/frontend/src/services/auditService.js): Service returning audit log records.

### `frontend/src/test/`
- **Path:** `frontend/src/test/`
- **Type:** Directory (Frontend Vitest Suite)
- **Purpose:** Unit and component tests for routing, session persistence, and document preview links.
- **Important contents:**
  - `session-persistence.test.ts`: Verifies saving, retrieving, updating, and corrupt-data recovery in `sessionStorage` (5/5 passed).
  - `document-preview-link.test.tsx`: Verifies `DocumentPreview` link rendering and fallback states (3/3 passed).
  - `app-routing.test.tsx`: Verifies TanStack Router matches root `/` and correctly treats `/directory` as unregistered (2/2 passed).
  - `setup.ts`: Configures `@testing-library/jest-dom` extensions.
- **Implementation status:** Implemented (all 10 vitest tests verified passing).
