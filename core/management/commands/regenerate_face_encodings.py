from __future__ import annotations

import logging
from pathlib import Path

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from core import face_utils
from core.models import Student

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Regenerate face encodings for students whose photos are present."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--force",
            action="store_true",
            help="Recalculate encodings even if one already exists.",
        )
        parser.add_argument(
            "--student",
            type=str,
            help="Limit regeneration to a specific student. Accepts primary key or username.",
        )

    def handle(self, *args, **options):
        force: bool = options["force"]
        student_filter: str | None = options.get("student")

        if not face_utils.FACE_RECOGNITION_AVAILABLE:
            self.stdout.write(self.style.ERROR("face_recognition library is not installed."))
            return

        queryset = Student.objects.select_related("user")
        if student_filter:
            if student_filter.isdigit():
                queryset = queryset.filter(pk=int(student_filter))
            else:
                queryset = queryset.filter(user__username=student_filter)

        processed = 0
        regenerated = 0
        skipped = 0

        for student in queryset.iterator():
            processed += 1

            if not student.photo:
                self.stdout.write(self.style.WARNING(f"Skipping {student} – no photo available."))
                skipped += 1
                continue

            if student.face_encodings and not force:
                skipped += 1
                continue

            try:
                with student.photo.open("rb") as handle:
                    image_array = face_utils.image_to_array(handle)
            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f"Missing photo file for {student}: {student.photo.name}"))
                skipped += 1
                continue
            except Exception as exc:  # pragma: no cover - safety net
                logger.warning("Failed reading photo for %s: %s", student.pk, exc)
                skipped += 1
                continue

            if image_array is None:
                skipped += 1
                continue

            encoding = face_utils.extract_first_encoding(image_array)
            if encoding is None:
                self.stdout.write(self.style.WARNING(f"No face detected for {student}."))
                skipped += 1
                continue

            student.face_encodings = encoding.tolist()
            with transaction.atomic():
                student.save(update_fields=["face_encodings"])
            regenerated += 1
            self.stdout.write(self.style.SUCCESS(f"Updated face encoding for {student}."))

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Processed {processed} student(s): {regenerated} regenerated, {skipped} skipped"
            )
        )
