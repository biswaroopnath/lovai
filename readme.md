# Local Voice AI [LoVAi] Project

## Overview

A lightweight voice AI application that supports text‑to‑speech, voice cloning, and customizable character prompts.

## Prerequisites

Currently tested on Windows 10.

- **Python 3.11**
- **KoboldCpp**: Download v1.108.2 from [GitHub](https://github.com/LostRuins/koboldcpp/releases/tag/v1.108.2) and place the `.exe` in the `kobolcpp/` folder.
- **Node.js v24.11.0**
- **npm v11.6.1**
- **Git v2.51.2.windows.1**

## Manual-Installation

```bash
# Clone the repository (if not already done)
git clone https://github.com/biswaroopnath/lovai.git
cd lovai
# Download KoboldCpp
# (Or manually download from: https://github.com/LostRuins/koboldcpp/releases/tag/v1.108.2)
# Make a models folder
mkdir models
# Make a koboldcpp folder
mkdir koboldcpp
curl -L -o koboldcpp/koboldcpp.exe https://github.com/LostRuins/koboldcpp/releases/download/v1.108.2/koboldcpp.exe
# Install required packages for python
python -m venv venv
venv\Scripts\Activate.ps1
# If you get error in running the above command, then run the following command:
# Set-ExecutionPolicy Unrestricted -Scope Process
# Then run the above command again
pip install -r requirements.txt
# Install front-end node modules
cd frontend
npm install
```

After this download your GGUF model and keep it in **`models/`** folder.

## Easy-Installation (Windows)

```bash
# Clone the repository (if not already done)
git clone https://github.com/biswaroopnath/lovai.git
cd lovai
./install_lovai.bat
```

After this download your GGUF model and keep it in **`models/`** folder.

## Usage

Run the main batch script on a new terminal (without the venv activated) to start the application:

```bash
./run_lovai.bat
```

## LoVAi Configuration

Edit `lovai_config.json` to change the below parameters:

- `character_folder`: Folder containing the character's prompt, template, sample.wav(optional) and payload. All of these are in `character` folder.
- `voice_clone`: Set to `true` to enable voice cloning.
- `sampling_time`: Time in seconds to sample the voice. If larger sample.wave file edit this parameter in seconds.
- `default_voice`: Default voice to use. Available voices by **pocket-tts** (in-built) are: `eponine`, `alba`, `marius`, `javert`, `jean`, `fantine`, `cosette` and `azelma`.
- `gpu_layers`: Number of layers to offload to the GPU. Usually 100 is enough for 12gb vram. -1 is for auto.
- `model`: GGUF Model to use. Place your model in `models/` folder.

## Character Customization

- Edit **`{{character_folder}}/prompt.txt`**, **`{{character_folder}}/default_template.txt`**, and **`{{character_folder}}/payload.json`** to change the character's personality, style, and response format. All of these are in `character` folder.
- For optional-voice-cloning (a bit slower) paste your voice sample in **`{{character_folder}}/sample.wav`** to change the voice (must be named as sample.wav). For larger sample.wave file edit `lovai_config.json`'s `sampling_time` parameter in seconds. Also set `voice_clone` to `true` in `lovai_config.json`.

## Model Management

- **Switch model**: Edit the model name in `lovai_config.json`.
- **Low‑VRAM model**: Download the Qwen 1.5B model from [Qwen-HuggingFace](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/blob/main/qwen2.5-1.5b-instruct-q4_0.gguf) and place it in `models/`.
- **High‑VRAM model (≈12 GB)**: Download the MN‑12B‑Mag‑Mell‑r1 (Uncensored) model from [MN-12B-Mag-Mell-R1-HuggingFace](https://huggingface.co/mradermacher/MN-12B-Mag-Mell-R1-GGUF/blob/main/MN-12B-Mag-Mell-R1.Q5_K_M.gguf) and place it in `models/`.

## Contributing

Feel free to open issues or submit pull requests for improvements, bug fixes, or new features.

## Architechture

- uses fastwishper large model for stt (gpu - accelerated)
- uses koboldcpp as backend for llm token streaming (gpu - accelerated if available)
- uses streamed data to generate tts using pocket-tts (runs on cpu)

## Features

- model can be changed easily
- can be run on low-end gpu
- can be run on cpu only (slower)
- can be run on gpu + cpu (fastest)
- can use custom character templates for character personality
- voice-cloning is available via pocket-tts
- enabled streaming from both llm and tts service so that you don't have to wait for the whole response to be generated before it starts speaking. This gives the feel of low latency (Helpfull for large model llms where output takes time to generate)
- can run only gguf models due to koboldcpp limitations
