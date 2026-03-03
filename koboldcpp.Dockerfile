# Use CUDA 12.1 runtime as base for GPU acceleration
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Install basic dependencies (curl for download, libgomp for llama.cpp)
RUN apt-get update && apt-get install -y \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Download the specific KoboldCpp Linux binary with CUDA support (v1.108.2)
RUN curl -L -o koboldcpp https://github.com/LostRuins/koboldcpp/releases/download/v1.108.2/koboldcpp-linux-x64-cuda121 \
    && chmod +x koboldcpp

# Expose KoboldCpp port
EXPOSE 5001

# The launcher script or the CMD will run this
# For Docker, we point to the volume-mounted models
# Use a generic name if needed or assume user provides it via compose command
CMD ["./koboldcpp", "--model", "/models/model.gguf", "--port", "5001", "--gpulayers", "100"]
