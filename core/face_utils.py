from __future__ import annotations

import logging
from typing import Any

import numpy as np
from PIL import Image, ImageOps

try:  # pragma: no cover - optional dependency
    import face_recognition  # type: ignore
except Exception:  # pragma: no cover - runtime import fallback
    face_recognition = None  # type: ignore

logger = logging.getLogger(__name__)

FACE_RECOGNITION_AVAILABLE = face_recognition is not None


def image_to_array(file_obj: Any) -> np.ndarray | None:
    """Return a RGB numpy array from a Django File-like object, handling EXIF rotation."""
    try:
        image = Image.open(file_obj)
    except Exception as exc:  # pragma: no cover - best effort logging
        logger.warning("Failed opening image for encoding: %s", exc)
        return None

    image = ImageOps.exif_transpose(image).convert("RGB")

    max_side = 1600
    if max(image.size) > max_side:
        image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

    return np.array(image)


def extract_first_encoding(image_array: np.ndarray) -> np.ndarray | None:
    """Return the first encoding using incremental fallbacks for tough images."""
    if face_recognition is None:
        return None

    encodings = list(face_recognition.face_encodings(image_array))  # type: ignore[attr-defined]
    if encodings:
        return encodings[0]

    hog_locations = face_recognition.face_locations(  # type: ignore[attr-defined]
        image_array,
        number_of_times_to_upsample=2,
        model="hog",
    )
    if hog_locations:
        encodings = face_recognition.face_encodings(  # type: ignore[attr-defined]
            image_array,
            known_face_locations=hog_locations,
        )
        if encodings:
            logger.debug("Generated encoding using hog fallback for %s face(s)", len(encodings))
            return encodings[0]

    try:
        cnn_locations = face_recognition.face_locations(  # type: ignore[attr-defined]
            image_array,
            number_of_times_to_upsample=0,
            model="cnn",
        )
    except Exception as exc:  # pragma: no cover - optional model support
        logger.debug("CNN face detection fallback failed: %s", exc, exc_info=True)
        cnn_locations = []

    if cnn_locations:
        encodings = face_recognition.face_encodings(  # type: ignore[attr-defined]
            image_array,
            known_face_locations=cnn_locations,
        )
        if encodings:
            logger.debug("Generated encoding using cnn fallback for %s face(s)", len(encodings))
            return encodings[0]

    return None
