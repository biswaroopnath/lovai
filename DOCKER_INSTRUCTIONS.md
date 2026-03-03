# Docker Deployment Instructions for LovAI 🚀

This project is now fully containerized with Docker and Docker Compose. This setup includes GPU support for NVIDIA cards using WSL2 (on Windows) or Linux.

## 📋 Prerequisites

1. **Docker Desktop** (with WSL2 backend enabled on Windows).
2. **NVIDIA Container Toolkit** installed.
    * [Installation Guide for Windows (WSL2)](https://docs.nvidia.com/cuda/wsl-user-guide/index.html#getting-started-with-cuda-on-wsl)
    * Ensure your NVIDIA drivers are up to date on the host.
    * [Installation Guide for Linux](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

## 🛠️ Getting Started

Open your terminal in the project root directory and run:

```powershell
docker-compose up --build
```

### ⛴️ Services Included

| Service | Description | Port |
| :--- | :--- | :--- |
| **frontend** | React/Vite web interface | [localhost:5173](http://localhost:5173) |
| **backend** | FastAPI (STT, TTS, Logic) | [localhost:8001](http://localhost:8001) |
| **koboldcpp** | LLM Inference Server | [localhost:5001](http://localhost:5001) |

## 🏗️ Technical Details

* **GPU Acceleration**: All services use NVIDIA GPU drivers for high-performance inference (`faster-whisper`, `KoboldCpp`).
* **Networking**: Services communicate internally via Docker's internal network (e.g., `backend` connects to `http://koboldcpp:5001`).
* **Persistent Data**: The `models/` directory is mounted to the `koboldcpp` container. Make sure your GGUF model (`MN-12B-Mag-Mell-R1.Q5_K_M.gguf` or similar) is in the root `models/` folder.

## 💡 Troubleshooting

* **Model Not Found**: If you use a different model filename, update the `command` section in `docker-compose.yml` for the `koboldcpp` service.
* **GPU Not Found**: Check if `nvidia-smi` works inside WSL2. If not, Docker won't be able to access the GPU.
* **Ports Busy**: Ensure no local instances of KoboldCpp (5001) or FastAPI (8001) are running outside Docker.

---
Now you can enjoy your fully containerized Voice AI environment!
