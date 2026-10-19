import logging
from typing import Optional, Tuple
from PIL import Image

logger = logging.getLogger(__name__)

try:
    import torch
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class HandwritingService:
    """
    Service for recognizing handwritten text using Microsoft TrOCR (microsoft/trocr-base-handwritten).
    Supports lazy model loading, local cache loading, and graceful fallbacks without blocking the application.
    """

    def __init__(self, model_name: str = "microsoft/trocr-base-handwritten"):
        self.model_name = model_name
        self.processor = None
        self.model = None
        self.initialized = False
        self.is_available = False
        self.load_error: Optional[str] = None

    def _initialize_model(self):
        if self.initialized:
            return
        if not TRANSFORMERS_AVAILABLE:
            msg = "transformers or torch not installed; TrOCR handwriting model disabled."
            logger.warning(f"[HandwritingService] {msg}")
            self.load_error = msg
            self.initialized = True
            self.is_available = False
            return

        try:
            logger.info(f"[HandwritingService] Checking local cache for TrOCR model: '{self.model_name}'...")
            # Attempt to load from local cache to ensure fast and non-blocking operation
            self.processor = TrOCRProcessor.from_pretrained(self.model_name, local_files_only=True)
            self.model = VisionEncoderDecoderModel.from_pretrained(self.model_name, local_files_only=True)
            self.model.eval()
            self.initialized = True
            self.is_available = True
            logger.info("[HandwritingService] TrOCR model and processor loaded successfully from local cache.")
        except Exception as e:
            self.load_error = f"{type(e).__name__}: {e}"
            logger.warning(
                f"[HandwritingService] TrOCR weights not cached locally ({self.load_error}). "
                f"Handwriting recognition will fall back to OCR line detection."
            )
            self.initialized = True
            self.is_available = False

    def is_model_loaded(self) -> bool:
        """Returns True if TrOCR model and processor are initialized and ready."""
        self._initialize_model()
        return self.is_available

    def predict_handwriting(self, image: Image.Image) -> Tuple[Optional[str], Optional[float]]:
        """
        Runs TrOCR model on a cropped image of handwritten text if loaded.
        Returns (text, confidence) or (None, None).
        """
        self._initialize_model()

        if not self.is_available or self.model is None or self.processor is None:
            logger.debug("[HandwritingService] Skipping TrOCR inference: model not available.")
            return None, None

        try:
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Check image dimensions to avoid zero-size or degenerate crops
            w, h = image.size
            if w < 8 or h < 8:
                logger.debug(f"[HandwritingService] Image crop too small ({w}x{h}); skipping TrOCR.")
                return None, None

            pixel_values = self.processor(images=image, return_tensors="pt").pixel_values
            with torch.no_grad():
                generated_ids = self.model.generate(pixel_values, max_new_tokens=50)

            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            cleaned_text = generated_text.strip()
            logger.info(f"[HandwritingService] TrOCR raw inference output: '{cleaned_text}'")

            if cleaned_text:
                return cleaned_text, None  # TrOCR does not output calibrated confidence by default
            return None, None
        except Exception as e:
            logger.error(f"[HandwritingService] Error during TrOCR inference: {e}")
            return None, None


# Global instance
handwriting_service = HandwritingService()
