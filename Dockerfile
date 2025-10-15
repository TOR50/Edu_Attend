FROM mambaorg/micromamba:1.5.10

# Ensure conda base env is active in RUN/CMD
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# Python env flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install Python and heavy libs via conda (prebuilt binaries): dlib, face_recognition, opencv, numpy, pillow, pip
RUN micromamba install -y -n base -c conda-forge \
    python=3.11 \
    dlib \
    face_recognition \
    opencv \
    numpy \
    pillow \
    pip \
 && micromamba clean -a -y

# Install pip dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . .

# Collect static at build time; media will be handled by storage backend
RUN python manage.py collectstatic --noinput

# Expose port (Render provides PORT env var)
EXPOSE 8000

# Entrypoint handles migrations then starts Gunicorn; run inside the conda env
CMD ["micromamba", "run", "-n", "base", "bash", "-lc", "bash /app/entrypoint.sh"]
