# Use NVIDIA CUDA 12.1 runtime as base for Faster-Whisper and PyTorch
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Avoid interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.10 and necessary system libraries for audio
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory to project root
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# We use pip to install the requirements directly
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the entire project code (excluding what's in .dockerignore)
COPY . .

# Expose the FastAPI port (8001)
EXPOSE 8001

# The backend/main.py expects to be run from the project root to resolve paths
CMD ["python3", "backend/main.py"]
