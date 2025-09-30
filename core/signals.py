import io
from PIL import Image
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student

try:
    import face_recognition  # type: ignore
except Exception:
    face_recognition = None

@receiver(post_save, sender=Student)
def generate_encoding_on_save(sender, instance: Student, created, **kwargs):
    if not instance.photo or face_recognition is None:
        return
    if instance.face_encodings:
        return
    try:
        with instance.photo.open('rb') as f:
            img = face_recognition.load_image_file(f)  # type: ignore[attr-defined]
            encs = face_recognition.face_encodings(img)  # type: ignore[attr-defined]
            if encs:
                instance.face_encodings = encs[0].tolist()
                instance.save(update_fields=["face_encodings"])
    except Exception:
        # best-effort only
        pass
