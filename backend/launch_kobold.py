import json
import os
import subprocess
import sys

def launch():
    # Get the directory where this script is located (backend folder)
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    # Project root is one level up from backend
    project_root = os.path.dirname(backend_dir)
    config_path = os.path.join(project_root, "lovai_config.json")

    print(f"[*] Backend Directory: {backend_dir}")
    print(f"[*] Project Root: {project_root}")
    print(f"[*] Config Path: {config_path}")
    
    # Defaults
    model_name = "MN-12B-Mag-Mell-R1.Q5_K_M.gguf"
    gpu_layers = 100
    
    # Load config
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                model_name = config.get("model", model_name)
                gpu_layers = config.get("gpu_layers", gpu_layers)
                print(f"[+] Loaded config: model={model_name}, gpu_layers={gpu_layers}")
        except Exception as e:
            print(f"[-] Error reading config: {e}. Using defaults.")
    else:
        print(f"[-] Config file not found at {config_path}. Using defaults.")

    # Paths relative to project root
    kobold_exe = os.path.join(project_root, "koboldcpp", "koboldcpp.exe")
    model_path = os.path.join(project_root, "models", model_name)
    
    print(f"[*] Kobold Executable Path: {kobold_exe}")
    print(f"[*] Model Path: {model_path}")

    if not os.path.exists(kobold_exe):
        print(f"[-] ERROR: KoboldCpp executable not found at {kobold_exe}")
        input("\nPress Enter to close this window...")
        return

    if not os.path.exists(model_path):
        print(f"[-] WARNING: Model file not found at {model_path}.")
        print("    KoboldCpp will start but will ask you to select a model manually.")

    # Construct command
    cmd = [
        kobold_exe,
        "--model", model_path,
        "--port", "5001",
        "--gpulayers", str(gpu_layers)
    ]
    
    print(f"\n[*] Launching KoboldCpp...")
    print(f"[*] Command: {' '.join(cmd)}\n")
    
    try:
        # We use Popen and wait to keep control 
        process = subprocess.Popen(cmd)
        print(f"[+] KoboldCpp started with PID: {process.pid}")
        print("[*] Keep this window open. KoboldCpp is running...")
        process.wait()
        print(f"\n[!] KoboldCpp has exited with code: {process.returncode}")
    except Exception as e:
        print(f"\n[-] CRITICAL ERROR launching KoboldCpp: {e}")
    
    input("\nPress Enter to close this window...")

if __name__ == "__main__":
    try:
        launch()
    except Exception as e:
        print(f"[-] SCRIPT CRASH: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to close this window...")
