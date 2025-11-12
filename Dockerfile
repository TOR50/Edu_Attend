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

# Ensure media directory exists and is writable by any runtime user
USER root
# Ensure app files are owned by runtime user and media folder exists
RUN chown -R mambauser:mambauser /app \
 && mkdir -p /app/media
USER mambauser

# Expose port (Render provides PORT env var)
EXPOSE 8000

# Ensure the conda env is active for any start command Render may inject
ENTRYPOINT ["micromamba", "run", "-n", "base", "bash", "-lc"]
# Default command runs our entrypoint; Render Start Command will override CMD but still pass through ENTRYPOINT
CMD ["bash /app/entrypoint.sh"]
