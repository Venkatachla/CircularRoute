import io
import numpy as np
from PIL import Image

try:
    import cv2
except ImportError:
    cv2 = None


def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """
    Loads a PIL Image from raw image bytes.
    """
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def preprocess_image_for_ocr(pil_img: Image.Image) -> np.ndarray:
    """
    Preprocesses PIL image to OpenCV format (BGR array) with contrast & subtle sharpening
    without removing handwritten lines.
    """
    img_np = np.array(pil_img)
    if cv2 is None:
        return img_np

    # Convert RGB to BGR for OpenCV
    bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # Optional mild contrast enhancement using CLAHE
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    return enhanced


def crop_image_region(pil_img: Image.Image, bbox: list[float], pad: int = 10) -> Image.Image:
    """
    Crops PIL image using bounding box [x0, y0, x1, y1] with configurable margin padding.
    """
    width, height = pil_img.size
    x0, y0, x1, y1 = bbox
    left = max(0, int(x0) - pad)
    top = max(0, int(y0) - pad)
    right = min(width, int(x1) + pad)
    bottom = min(height, int(y1) + pad)

    return pil_img.crop((left, top, right, bottom))
