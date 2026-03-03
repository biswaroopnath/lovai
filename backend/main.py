import os
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

import requests
import json
import shutil
import tempfile
from fastapi import FastAPI, HTTPException, Response, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from tts_service import TTSService
from faster_whisper import WhisperModel, BatchedInferencePipeline
from history import reset_history, update_prompt, finalize_turn, get_config, get_character_paths

# Configuration is now loaded dynamically via history.get_config()

app = FastAPI()

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Pocket TTS Service
device = 'cpu'
print(f"Initializing Pocket TTS Service on {device}...")
try:
    tts_service = TTSService(device=device)
    print("Pocket TTS Service initialized successfully.")
except Exception as e:
    print(f"Failed to initialize Pocket TTS Service: {e}")
    tts_service = None

# Initialize Faster-Whisper
try:
    print("Initializing Faster-Whisper Large-v2 Pipeline on CUDA...")
    whisper_model = WhisperModel("large-v2", device="cuda", compute_type="int8")
    batched_whisper_model = BatchedInferencePipeline(model=whisper_model)
    print("Faster-Whisper Pipeline initialized successfully.")
except Exception as e:
    print(f"Failed to initialize Faster-Whisper Pipeline: {e}")
    batched_whisper_model = None

import httpx
import re
import asyncio

# KoboldCpp API URLs
KOBOLD_BASE_URL = os.getenv("KOBOLD_BASE_URL", "http://localhost:5001")
KOBOLD_GENERATE_URL = f"{KOBOLD_BASE_URL}/api/v1/generate"
KOBOLD_STREAM_URL = f"{KOBOLD_BASE_URL}/api/extra/generate/stream"

class ChatRequest(BaseModel):
    prompt: str
    max_length: Optional[int] = 120
    temperature: Optional[float] = 0.7
    voice: Optional[str] = None

async def get_kobold_stream(payload):
    """Generator for streaming tokens from KoboldCpp with extra robustness."""
    print(f"[KoboldStream] Connecting to {KOBOLD_STREAM_URL}...")
    
    # Ensure nested payload has stream enabled
    payload["stream"] = True
    
    async with httpx.AsyncClient(timeout=120) as client:
        try:
            async with client.stream("POST", KOBOLD_STREAM_URL, json=payload) as response:
                print(f"[KoboldStream] Status: {response.status_code}")
                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"[KoboldStream] Error detail: {error_text.decode()}")
                    return

                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Log the raw line for debugging
                    print(f"[KoboldStream] Raw: {line}")
                    
                    if line.startswith("data: "):
                        try:
                            json_str = line[6:].lstrip()
                            if not json_str: continue
                            
                            data = json.loads(json_str)
                            # KoboldCpp uses 'text', some wrappers use 'token' or 'content'
                            token = data.get("text") or data.get("token") or ""
                            
                            if token:
                                print(f"[KoboldToken]: {token}")
                                yield token
                        except json.JSONDecodeError as e:
                            print(f"[KoboldStream] JSON Error: {e} in {line}")
                            continue
                print("[KoboldStream] Connection closed by server.")
        except Exception as e:
            print(f"[KoboldStream] HTTP/Connection Exception: {e}")
            yield ""

async def token_to_sentence_stream(token_generator):
    """Groups tokens into sentences for better TTS flow with initial buffering."""
    buffer = ""
    # Punctuation that likely ends a sentence, including newlines
    sentence_endings = re.compile(r'([.!?\n]+)(\s+|$)', re.MULTILINE)
    
    print("[Sentence Splitter] Initialized.")
    
    # Optional: Initial delay to ensure we have content before starting
    # The user asked for a "second delay", let's do 0.5s for responsiveness
    await asyncio.sleep(0.5)

    try:
        async for token in token_generator:
            if token is None: continue
            buffer += token
            
            while True:
                # Look for sentence endings
                match = sentence_endings.search(buffer)
                if match:
                    split_point = match.end(1)
                    sentence = buffer[:split_point].strip()
                    if sentence:
                        print(f"\n[Sentence Splitter] Yielding: {sentence}")
                        yield sentence
                    buffer = buffer[split_point:].lstrip()
                else:
                    # Buffer 100 chars if no punctuation, to keep it moving
                    if len(buffer) > 100:
                        last_space = buffer.rfind(' ')
                        if last_space > 30: 
                            sentence = buffer[:last_space].strip()
                            print(f"\n[Sentence Splitter] Fallback Yield: {sentence}")
                            yield sentence
                            buffer = buffer[last_space:].lstrip()
                            continue
                    break
    except Exception as e:
        print(f"\n[Sentence Splitter] ERROR: {e}")
    finally:
        if buffer.strip():
            print(f"\n[Sentence Splitter] Final Yield: {buffer.strip()}")
            yield buffer.strip()

@app.post("/chat")
async def chat(request: ChatRequest):
    """Standard non-streaming chat proxy."""
    try:
        # Load dynamic paths
        paths = get_character_paths()
        payload_path = paths["payload"]
        prompt_path = paths["prompt"]

        update_prompt(request.prompt)

        with open(prompt_path, "r", encoding="utf-8") as f:
            full_prompt = f.read().strip()

        with open(payload_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        payload["prompt"] = full_prompt
        if request.max_length: payload["max_length"] = request.max_length
        if request.temperature: payload["temperature"] = request.temperature

        response = requests.post(KOBOLD_GENERATE_URL, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()
        text = data.get("results", [{}])[0].get("text", "").strip()

        finalize_turn(text)
        return {"response": text}

    except Exception as e:
        print(f"Error calling KoboldCpp: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat_voice")
async def chat_voice(prompt: str, voice: Optional[str] = None, max_length: int = 120, temperature: float = 0.7):
    """
    Streaming LLM + TTS for instantaneous voice response.
    Returns a stream of raw audio data (WAV) as the LLM generates tokens.
    Usage: GET /chat_voice?prompt=...&voice=eponine
    """
    if not tts_service:
        raise HTTPException(status_code=500, detail="TTSService not initialized")

    try:
        # Load dynamic paths and config
        config = get_config()
        paths = get_character_paths()
        payload_path = paths["payload"]
        prompt_path = paths["prompt"]

        if voice is None:
            voice = config.get("default_voice", "eponine")

        # Initialize history
        update_prompt(prompt)

        with open(prompt_path, "r", encoding="utf-8") as f:
            full_prompt = f.read().strip()

        with open(payload_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        payload["prompt"] = full_prompt
        payload["max_length"] = max_length
        payload["temperature"] = temperature

        async def audio_generator():
            try:
                # 1. Send the WAV header once
                print("[AudioGen] Sending WAV header...")
                header = tts_service.get_wav_header()
                yield header

                full_text = []
                token_count = 0
                
                # 2. Start LLM stream -> sentence stream -> TTS stream
                print(f"[AudioGen] Starting Kobold stream for prompt: {prompt}...")
                tokens = get_kobold_stream(payload)
                sentences = token_to_sentence_stream(tokens)
                
                async for sentence in sentences:
                    print(f"\n[AudioGen] Processing sentence: \"{sentence}\"")
                    full_text.append(sentence)
                    
                    chunk_in_sentence = 0
                    # We use the sync-generator within an async context
                    for pcm_chunk in tts_service.generate_pcm_stream(sentence, voice_name=voice):
                        chunk_in_sentence += 1
                        if len(pcm_chunk) > 0:
                            yield pcm_chunk
                        await asyncio.sleep(0) # Yield control to the event loop
                    
                    print(f"[AudioGen] Finished sentence. Yielded {chunk_in_sentence} PCM chunks.")
                    token_count += 1
                
                if not full_text:
                    print("[AudioGen] WARNING: No text was generated by the LLM!")
                else:
                    # 3. Finalize history after LLM is done
                    final_response = " ".join(full_text)
                    print(f"[AudioGen] Finalizing turn with {len(full_text)} sentences.")
                    finalize_turn(final_response)
                
                print("[AudioGen] Audio generation loop finished.")
            except Exception as gen_err:
                print(f"[AudioGen] CRITICAL ERROR in generator: {gen_err}")
                import traceback
                traceback.print_exc()

        return StreamingResponse(
            audio_generator(),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "inline",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )

    except Exception as e:
        print(f"Error in chat_voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tts")
async def tts(text: str, voice: Optional[str] = None):
    """
    Pocket TTS endpoint.
    Processes text into speech using the TTSService.
    """
    if not tts_service:
        raise HTTPException(status_code=500, detail="TTSService not initialized")
    
    if voice is None:
        config = get_config()
        voice = config.get("default_voice", "eponine")
    
    try:
        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            temp_path = tmp.name
        
        # Generate audio
        tts_service.generate(text, voice_name=voice, output_path=temp_path)
        
        # Read the file and return as response
        with open(temp_path, "rb") as f:
            audio_data = f.read()
            
        # Clean up
        os.remove(temp_path)
        
        return Response(content=audio_data, media_type="audio/wav")
    except Exception as e:
        print(f"TTS Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tts_stream")
async def tts_stream(text: str, voice: Optional[str] = None):
    """
    Pocket TTS streaming endpoint.
    Processes text into speech and streams audio chunks for low latency.
    """
    if not tts_service:
        raise HTTPException(status_code=500, detail="TTSService not initialized")
    
    if voice is None:
        config = get_config()
        voice = config.get("default_voice", "eponine")
    
    try:
        return StreamingResponse(
            tts_service.generate_stream(text, voice_name=voice),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "inline",
                "Cache-Control": "no-cache",
                "X-Content-Type-Options": "nosniff",
                "Connection": "keep-alive",
                "Accept-Ranges": "none"
            }
        )
    except Exception as e:
        print(f"TTS Stream Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stt")
async def stt(file: UploadFile = File(...)):
    """Faster-whisper STT endpoint."""
    if not batched_whisper_model:
        raise HTTPException(status_code=500, detail="Faster-Whisper pipeline not initialized")
    
    try:
        # Save temp audio file
        suffix = os.path.splitext(file.filename)[1]
        if not suffix:
            suffix = ".webm"
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
            shutil.copyfileobj(file.file, temp_audio)
            temp_audio_path = temp_audio.name
            
        segments, info = batched_whisper_model.transcribe(temp_audio_path, batch_size=8)
        
        text = "".join([segment.text for segment in segments]).strip()
        
        # clean up temp file
        os.remove(temp_audio_path)
        
        return {"text": text}
    
    except Exception as e:
        print(f"STT Error: {e}")
        if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Reset history before launching the application
    reset_history()
    # Changed to 8001 to match run_voice_ai.bat and avoid confusion
    uvicorn.run(app, host="0.0.0.0", port=8001)
