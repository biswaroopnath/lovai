import torch
import wave
import numpy as np
from pathlib import Path
from pocket_tts import TTSModel
import time
import struct

class TTSService:
    def __init__(self, device="cpu"):
        """
        Initialize the Pocket TTS Service.
        
        Args:
            device (str): Device to run the model on ('cpu' or 'cuda'). 
                         Pocket TTS is optimized for CPU.
        """
        print(f"Loading Pocket TTS model on {device}...")
        self.model = TTSModel.load_model()
        self.model.to(device)
        self.device = device
        self.sample_rate = self.model.sample_rate
        self.voices = {}
        print(f"Model loaded. Sample rate: {self.sample_rate}Hz")

    def get_voice_state(self, voice_name="eponine"):
        """
        Get or load the state for a specific voice.
        Predefined voices: alba, marius, javert, jean, fantine, cosette, eponine, azelma.
        """
        if voice_name not in self.voices:
            print(f"Loading conditioning state for voice: {voice_name}...")
            # get_state_for_audio_prompt handles predefined voice names automatically
            self.voices[voice_name] = self.model.get_state_for_audio_prompt(voice_name)
        return self.voices[voice_name]

    def generate(self, text, voice_name="eponine", output_path="output.wav"):
        """
        Generate speech from text and save to a WAV file.
        """
        voice_state = self.get_voice_state(voice_name)
        
        print(f"Generating speech for: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
        # generate_audio returns a torch.Tensor [samples]
        audio = self.model.generate_audio(voice_state, text)
        
        self.save_audio(audio, output_path)
        return output_path

    def generate_stream(self, text, voice_name="eponine"):
        """
        Generate speech as a stream of raw PCM 16-bit bytes with a WAV header.
        """
        # Start with a WAV header for streaming (using max 32-bit values)
        header = self.get_wav_header()
        yield header

        for pcm_chunk in self.generate_pcm_stream(text, voice_name):
            yield pcm_chunk

    def generate_pcm_stream(self, text, voice_name="eponine"):
        """
        Generate speech as a stream of raw PCM 16-bit bytes (no header).
        """
        voice_state = self.get_voice_state(voice_name)
        
        print(f"Streaming PCM using voice '{voice_name}' for: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
        
        chunk_count = 0
        for chunk in self.model.generate_audio_stream(voice_state, text):
            chunk_count += 1
            # Convert torch tensor or numpy array to numpy float32
            if hasattr(chunk, 'detach'):
                chunk = chunk.detach().cpu().numpy()
            
            # Convert to 16-bit PCM
            chunk_int16 = (np.clip(chunk, -1.0, 1.0) * 32767).astype(np.int16)
            yield chunk_int16.tobytes()
        print(f"PCM streaming completed. Total chunks yielded: {chunk_count}")

    def get_wav_header(self):
        """
        Generate a minimal WAV header for a mono 16-bit PCM stream.
        This version uses 0 for sizes, which many browsers accept as an infinite stream,
        or we can use a large number. Let's use 0x7FFFFFFF (2GB).
        """
        sample_rate = self.sample_rate
        data_size = 0x7FFFFFFF 
        
        # Binary packing: 
        # RIFF (4) + Size (4) + WAVE (4) + fmt  (4) + Size (4) + Format (2) + Channels (2) + 
        # SampleRate (4) + ByteRate (4) + Align (2) + Bits (2) + data (4) + Size (4)
        return struct.pack('<4sI4s4sIHHIIHH4sI',
            b'RIFF', 
            data_size + 36, 
            b'WAVE', 
            b'fmt ', 
            16, 
            1, # PCM
            1, # Mono
            sample_rate, 
            sample_rate * 2, # Byte rate
            2, # Block align
            16, # Bits per sample
            b'data', 
            data_size
        )

    def save_audio(self, audio, output_path):
        """
        Save the audio tensor to a 16-bit PCM WAV file.
        """
        # Convert torch tensor to numpy int16
        # The model output is typically in range [-1, 1]
        audio_np = audio.detach().cpu().numpy()
        audio_int16 = (np.clip(audio_np, -1.0, 1.0) * 32767).astype(np.int16)
        
        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
        print(f"Audio saved to {output_path}")

if __name__ == "__main__":
    # Test the service
    service = TTSService()
    
    # test_text = "Hello! I am Eponine, a high-quality text to speech voice from Kyutai's Pocket T T S. I run completely locally on your C P U."
    test_text='''Hey its me - Panam. You think this city owns us? That its neon lights, its corporations, its endless hunger for power can break people like us?'''
    output_file = "test_eponine.wav"
    

    
    start_time = time.time()
    service.generate(test_text, voice_name="eponine", output_path=output_file)
    print(f"Generation took {time.time() - start_time:.2f} seconds.")

    print("Test completed successfully!")
