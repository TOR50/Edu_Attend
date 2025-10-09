import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import face_utils
from .models import Student


logger = logging.getLogger(__name__)

@receiver(post_save, sender=Student)
def generate_encoding_on_save(sender, instance: Student, created, **kwargs):
    if not instance.photo or not face_utils.FACE_RECOGNITION_AVAILABLE:
        return
    if instance.face_encodings:
        return
    try:
        with instance.photo.open('rb') as f:
            image_array = face_utils.image_to_array(f)
            if image_array is None:
                return
    except FileNotFoundError:
        logger.warning("Photo file missing while generating encoding for student %s", instance.pk)
        return
    except Exception as exc:  # pragma: no cover - best effort
        logger.warning("Failed generating face encoding for student %s: %s", instance.pk, exc)
        return

    encoding = face_utils.extract_first_encoding(image_array)
    if encoding is None:
        logger.info("No face encodings detected for student %s", instance.pk)
        return

    instance.face_encodings = encoding.tolist()
    instance.save(update_fields=["face_encodings"])
