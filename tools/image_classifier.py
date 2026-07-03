"""
image_classifier.py — Pre-processing and validation for plant disease images.
PIL + OpenCV preprocessing before passing to Granite Vision.
"""

import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from loguru import logger

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available — using PIL-only preprocessing.")

from PIL import Image, ImageEnhance
from config import ActiveConfig


class ImageClassifier:
    """Image validation, preprocessing, and quality enhancement."""

    MAX_SIZE = (1024, 1024)
    MIN_SIZE = (100, 100)

    def __init__(self):
        self.upload_folder = Path(ActiveConfig.UPLOAD_FOLDER)
        self.upload_folder.mkdir(parents=True, exist_ok=True)

    def validate_and_save(self, file) -> Dict[str, Any]:
        """
        Validate an uploaded FileStorage object, preprocess,
        save to disk, and return metadata.
        """
        # Security: check extension
        filename = file.filename or ""
        ext = Path(filename).suffix.lower().lstrip(".")
        if ext not in ActiveConfig.ALLOWED_EXTENSIONS:
            return {"success": False, "error": f"File type .{ext} not allowed. Use jpg, jpeg, or png."}

        # Generate safe filename
        safe_name = f"{uuid.uuid4().hex}.jpg"
        save_path = self.upload_folder / safe_name

        try:
            img = Image.open(file.stream).convert("RGB")

            # Size validation
            if img.size[0] < self.MIN_SIZE[0] or img.size[1] < self.MIN_SIZE[1]:
                return {"success": False, "error": "Image too small. Minimum 100×100 pixels required."}

            # Preprocess
            img = self._preprocess(img)
            img.save(str(save_path), "JPEG", quality=92)

            return {
                "success": True,
                "filename": safe_name,
                "path": str(save_path),
                "original_name": filename,
                "size": os.path.getsize(save_path),
                "dimensions": img.size,
            }
        except Exception as exc:
            logger.error(f"Image processing failed: {exc}")
            return {"success": False, "error": f"Image processing error: {exc}"}

    def _preprocess(self, img: Image.Image) -> Image.Image:
        """Resize, enhance contrast and sharpness for better model input."""
        img.thumbnail(self.MAX_SIZE, Image.LANCZOS)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.3)
        return img

    def enhance_with_cv2(self, image_path: str) -> Optional[str]:
        """Apply CLAHE for better disease visibility (optional enhancement)."""
        if not CV2_AVAILABLE:
            return image_path
        try:
            img = cv2.imread(image_path)
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
            enhanced_path = image_path.replace(".jpg", "_enhanced.jpg")
            cv2.imwrite(enhanced_path, enhanced)
            return enhanced_path
        except Exception as exc:
            logger.warning(f"CLAHE enhancement failed: {exc}")
            return image_path

    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """Return basic metadata for a stored image."""
        try:
            img = Image.open(image_path)
            return {
                "path": image_path,
                "size_bytes": os.path.getsize(image_path),
                "dimensions": img.size,
                "mode": img.mode,
            }
        except Exception as exc:
            return {"error": str(exc)}
