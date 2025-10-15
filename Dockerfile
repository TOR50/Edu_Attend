FROM ageitgey/face_recognition:latest

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (if you need additional, add here)
# ageitgey/face_recognition already includes dlib, face_recognition, OpenCV, Python

# Install Python deps first for better layer caching
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . .

# Collect static at build time; media will be handled by storage backend
RUN python manage.py collectstatic --noinput

# Expose port (Render provides PORT env var)
EXPOSE 8000

# Entrypoint handles migrations then starts Gunicorn
RUN chmod +x ./entrypoint.sh
CMD ["./entrypoint.sh"]
