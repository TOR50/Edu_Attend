"""
This service handles all face recognition and encoding logic.
"""
import face_recognition
import numpy as np
from .models import Student, FaceSample, AttendanceRecord, SchoolClass, AcademicYear
from django.utils import timezone
from django.db import transaction

def load_known_faces_for_class(class_id: int):
    """
    Load all known face encodings for a given class.
    This improves accuracy by using multiple samples per student.
    """
    known_face_encodings = []
    known_face_metadata = []

    try:
        school_class = SchoolClass.objects.get(id=class_id)
        students = school_class.students.all()
    except SchoolClass.DoesNotExist:
        return [], []


    for student in students:
        # Use the primary face encoding first if it exists
        if student.face_encodings:
            try:
                known_face_encodings.append(np.array(student.face_encodings))
                known_face_metadata.append({"student_id": student.pk, "name": student.get_full_name()})
            except (ValueError, TypeError):
                continue # Skip if encoding is invalid

        # Then add encodings from all face samples
        for sample in student.samples.all():
            try:
                image = face_recognition.load_image_file(sample.image.path)
                # Assuming one face per sample for simplicity
                encoding = face_recognition.face_encodings(image)[0]
                known_face_encodings.append(encoding)
                known_face_metadata.append({"student_id": student.pk, "name": student.get_full_name()})
            except (IndexError, FileNotFoundError):
                # Handle cases where a face isn't found or file is missing
                continue
                
    return known_face_encodings, known_face_metadata

def find_matches_in_frame(frame_rgb, known_face_encodings, known_face_metadata, tolerance=0.4):
    """
    Recognizes faces in a single video frame and returns match data.
    Does NOT modify the database.
    """
    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(frame_rgb)
    face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)
    
    detected_faces = []

    for face_encoding, face_location in zip(face_encodings, face_locations):
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=tolerance)
        
        # Use the best match
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        
        best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else -1
        
        top, right, bottom, left = face_location
        detection_result = {
            "box": [top, right, bottom, left],
            "metric": float(face_distances[best_match_index]) if best_match_index != -1 else None,
            "student_id": None,
            "name": "Unknown"
        }

        if best_match_index != -1 and matches[best_match_index]:
            metadata = known_face_metadata[best_match_index]
            detection_result["student_id"] = metadata["student_id"]
            detection_result["name"] = metadata["name"]

        detected_faces.append(detection_result)
            
    return detected_faces

@transaction.atomic
def mark_attendance_for_matches(matched_students, class_id):
    """
    Mark attendance for a list of student IDs for a specific class.
    Avoids duplicate entries for the same day.
    """
    today = timezone.now().date()
    try:
        school_class = SchoolClass.objects.get(id=class_id)
        active_academic_year = school_class.academic_year
    except SchoolClass.DoesNotExist:
        return 0

    if not active_academic_year:
        return 0 # No active academic year found for this class

    marked_count = 0
    for student_id, confidence in matched_students:
        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            continue

        # Ensure student is actually in the class
        if student not in school_class.students.all():
            continue

        # Get or create the record
        record, created = AttendanceRecord.objects.get_or_create(
            student=student,
            school_class=school_class,
            date=today,
            academic_year=active_academic_year,
            defaults={'status': 'present', 'confidence': confidence}
        )

        # If record already existed but wasn't 'present', update it.
        if not created and record.status != 'present':
            record.status = 'present'
            record.confidence = confidence
            record.save()
        
        if created:
            marked_count += 1
            
    return marked_count

