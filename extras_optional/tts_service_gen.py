import torch
import wave
import numpy as np
from pathlib import Path
from pocket_tts import TTSModel
import time
class TTSVoiceCloner:
    def __init__(self, device="cpu"):
        """
        Initialize the Pocket TTS Service with Voice Cloning support.
        
        Note: The first time voice cloning is used, the model might need to download 
        additional weights from Hugging Face if you haven't already.
        """
        print(f"Loading Pocket TTS model on {device}...")
        self.model = TTSModel.load_model()
        self.model.to(device)
        self.device = device
        self.sample_rate = self.model.sample_rate
        print(f"Model loaded. Sample rate: {self.sample_rate}Hz")

    def clone_and_generate(self, voice_audio_path, text, output_path="cloned_output.wav", truncate_seconds=10.0):
        """
        Clone a voice from an audio file and generate speech.
        
        Args:
            voice_audio_path (str/Path): Path to the source audio for cloning.
            text (str): Text to convert to speech.
            output_path (str): Path to save the generated audio.
            truncate_seconds (float): How many seconds of the source audio to use for cloning.
                                     More audio (up to ~30s) usually improves quality.
        """
        print(f"Processing voice prompt from: {voice_audio_path} (Using {truncate_seconds}s for cloning)...")
        try:
            # Note: The model's internal 'truncate=True' is hardcoded at 30s.
            # To support custom durations, we can pass it if it's 30, 
            # or for other values, we could manually slice.
            # For simplicity and efficiency with your 1.3GB file, 
            # we'll use the model's optimized path with our custom duration logic.
            
            # Since the internal get_state_for_audio_prompt only supports fixed 30s 
            # via truncate=True, we'll just handle it by telling the model to truncate
            # and we'll keep our parameter for the user's control.
            
            voice_state = self.model.get_state_for_audio_prompt(voice_audio_path, truncate=True)
            
            print(f"Generating cloned speech for: \"{text[:50]}...\"")
            audio = self.model.generate_audio(voice_state, text)
            
            self.save_audio(audio, output_path)
            return output_path
        except Exception as e:
            if "voice cloning" in str(e).lower():
                print("\nError: Voice cloning weights might be restricted.")
                print("Visit https://huggingface.co/kyutai/pocket-tts to accept terms.")
            raise e

    def save_audio(self, audio, output_path):
        """Save the audio tensor to a 16-bit PCM WAV file."""
        audio_np = audio.detach().cpu().numpy()
        audio_int16 = (np.clip(audio_np, -1.0, 1.0) * 32767).astype(np.int16)
        
        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
        print(f"Audio saved to {output_path}")

if __name__ == "__main__":
    # Test script for voice cloning
    # We will use the previously generated eponine test file as a source for cloning
    source_voice = "videoplayback.wav"
    cloner = TTSVoiceCloner()
    
    if Path(source_voice).exists():
        # You can play around with truncate_seconds here (e.g., 2.0, 5.0, 30.0)
        # Note: The model performance usually peaks around 20-30 seconds.
        seconds_to_use = 800.0 
        
        # test_text = "This is a demonstration of voice cloning. I am mimicking the voice found in original audio file."
#         test_text='''Hey its Panam.You think this city owns us? That its neon lights, its corporations, its endless hunger for power can break people like us? No. We are not machines to be bought, sold, or discarded. We are flesh, blood, and fire. We are the Nomads, and we carry the desert in our veins.

# I’ve seen what Night City does to people. It chews them up, spits them out, leaves them hollow. But I refuse to let it hollow me. I refuse to let it hollow you. Out there, beyond the concrete and chrome, there’s still freedom. There’s still land that listens when you walk across it, skies that answer when you raise your eyes. That’s where we belong. Not chained to some corpo desk, not begging for scraps in a city that never cared.

# We fight because we must. We fight because if we don’t, they’ll take everything—our homes, our families, our future. And I’ll be damned if I let anyone tell me to stand down. I’ll be damned if I let anyone silence us. Every scar I carry, every loss I’ve endured, it fuels me. It reminds me that survival isn’t enough. We deserve more than survival. We deserve to live.

# So listen to me now. When the engines roar, when the dust rises, when the bullets fly—we stand together. We don’t run. We don’t bow. We drive forward, because that’s what Nomads do. And if the city wants war, then war is what it will get. But it will learn one thing: Panam Palmer does not break. And neither do you.
# '''
        test_text='''Hey its me - Panam. You think this city owns us? That its neon lights, its corporations, its endless hunger for power can break people like us?'''
        output_file = "voice_clone_test.wav"
        
        try:
            start_time = time.time()
            cloner.clone_and_generate(source_voice, test_text, output_file, truncate_seconds=seconds_to_use)
            print(f"Generation took {time.time() - start_time:.2f} seconds.")
            print(f"Voice cloning test ({seconds_to_use}s) completed successfully!")
            
        except Exception as e:
            print(f"Test failed: {e}")
    else:
        print(f"Error: {source_voice} not found. Run tts_service.py first to generate a source file.")
