import os
import json
import time
import requests
import winsound
import re
import sys

# Add current directory to path so we can import history
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from history import get_default_template, get_config
except ImportError as e:
    print(f"[-] Failed to import history: {e}")
    sys.exit(1)

def wait_for_service(url, name, timeout=300):
    print(f"[*] Waiting for {name} to be ready at {url}...")
    start_time = time.time()
    attempts = 0
    while time.time() - start_time < timeout:
        attempts += 1
        try:
            response = requests.get(url, timeout=5)
            # Any status code (200, 404, etc) means the server is UP and responding
            print(f"[+] {name} is ready after {attempts} attempts!")
            return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            if attempts % 5 == 0:
                print(f"    - {name} still initializing (attempt {attempts})...")
            pass
        except Exception as e:
            print(f"    - Unexpected error checking {name}: {e}")
            pass
        time.sleep(2)
    print(f"[-] {name} failed to respond within {timeout} seconds.")
    return False

def extract_greeting():
    config = get_config()
    char_name = config.get("character_name", "Panam Palmer")
    
    content = get_default_template()
    
    # Extract text between {{[OUTPUT]}}Character Name: and {{[INPUT]}}
    # The template usually looks like: {{[OUTPUT]}}Panam Palmer: Hi there...{{[INPUT]}}
    pattern = rf"\{{{{\[OUTPUT\]}}}}{re.escape(char_name)}:\s*(.*?)\{{{{\[INPUT\]}}}}"
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        greeting = match.group(1).strip()
        return greeting
    else:
        # Fallback: find anything between the first {{[OUTPUT]}} and {{[INPUT]}}
        pattern_fallback = r"\{{{{\[OUTPUT\]}}}}.*?:\s*(.*?)\{{{{\[INPUT\]}}}}"
        match_fallback = re.search(pattern_fallback, content, re.DOTALL)
        if match_fallback:
            return match_fallback.group(1).strip()
            
    print("[-] Could not parse greeting from template.")
    return None

def main():
    print("\n--- Voice AI Startup Greeting Monitor ---")
    
    # 1. Wait for services
    kobold_up = wait_for_service("http://localhost:5001/api/v1/model", "KoboldCpp")
    backend_up = wait_for_service("http://localhost:8001/", "Backend API")
    frontend_up = wait_for_service("http://localhost:5173/", "Frontend (Vite)")
    
    if not (kobold_up and backend_up):
        print("[-] Critical services failed to start properly. Skipping greeting.")
        return

    if not frontend_up:
        print("[!] Warning: Frontend might not be ready yet, but continuing...")

    # 2. Get greeting text
    greeting = extract_greeting()
    if not greeting:
        print("[-] No greeting text found in template.")
        return
        
    print(f"[+] Character Greeting: \"{greeting[:100]}...\"")
    
    # 3. Request TTS from our own backend
    try:
        print("[*] Generating greeting audio...")
        # Use /tts endpoint
        response = requests.get("http://localhost:8001/tts", params={"text": greeting}, timeout=60)
        
        if response.status_code == 200:
            # Save to temporary file in the project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            temp_wav = os.path.join(project_root, "startup_greeting.wav")
            
            with open(temp_wav, "wb") as f:
                f.write(response.content)
            
            print("[*] Playing greeting...")
            winsound.PlaySound(temp_wav, winsound.SND_FILENAME)
            
            # Clean up
            try:
                os.remove(temp_wav)
            except:
                pass
            print("[+] Greeting finished.")
        else:
            print(f"[-] TTS Request failed with status: {response.status_code}")
            print(f"[-] Response: {response.text}")
    except Exception as e:
        print(f"[-] Error during greeting sequence: {e}")

if __name__ == "__main__":
    main()
