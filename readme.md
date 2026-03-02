# Local Voice AI [LoVAi] Project

## Overview

A lightweight voice AI application that supports text‑to‑speech, voice cloning, and customizable character prompts.

## Prerequisites

- **Python 3.11**
- **KoboldCpp**: Download v1.108.2 from [GitHub](https://github.com/LostRuins/koboldcpp/releases/tag/v1.108.2) and place the `.exe` in the `kobolcpp/` folder.
- Install dependencies:

  ```bash
  python -m venv venv
  venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

## Manual-Installation

```bash
# Clone the repository (if not already done)
git clone https://github.com/biswaroopnath/lovai.git
cd lovai
# Download KoboldCpp
# (Or manually download from: https://github.com/LostRuins/koboldcpp/releases/tag/v1.108.2)
curl -L -o kobolcpp/koboldcpp.exe https://github.com/LostRuins/koboldcpp/releases/download/v1.108.2/koboldcpp.exe
# Install required packages
pip install -r requirements.txt
# Install front-end
cd frontend
npm install
```

After this download your GGUF model and keep it in **`kobolcpp/koboldcpp_gguf_models/`** folder.

## Easy-Installation

```bash
# Clone the repository (if not already done)
./install.bat
```

After this download your GGUF model and keep it in **`kobolcpp/koboldcpp_gguf_models/`** folder.

## Usage

Run the main batch script on a new terminal (without the venv activated) to start the application:

```bash
./run_voice_ai.bat
```

## Optional: Voice Cloning

Use the `tts_service_gen.py` script to generate cloned voices. See its documentation for parameter options.

## Character Customization

- Edit **`backend/prompt.txt`**, **`backend/default_template.txt`**, and **`kobolcpp/payload.txt`** to change the character's personality, style, and response format.

## Model Management

- **Switch model**: Edit the model name in `run_voice_ai.bat`.
- **Low‑VRAM model**: Download the Qwen 1.5B model from [HuggingFace](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/blob/main/qwen2.5-1.5b-instruct-q4_0.gguf) and place it in `koboldcpp/koboldcpp_gguf_models/`.
- **High‑VRAM model (≈12 GB)**: Download the MN‑12B‑Mag‑Mell‑r1 (Uncensored) model from [HuggingFace](https://huggingface.co/mradermacher/MN-12B-Mag-Mell-R1-GGUF/blob/main/MN-12B-Mag-Mell-R1.Q5_K_M.gguf) and place it in the same directory.

## Contributing

Feel free to open issues or submit pull requests for improvements, bug fixes, or new features.
