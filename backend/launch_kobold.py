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
                print(f"Loaded config: model={model_name}, gpu_layers={gpu_layers}")
        except Exception as e:
            print(f"Error reading config: {e}. Using defaults.")
    else:
        print(f"Config file not found at {config_path}. Using defaults.")

    # Paths relative to project root
    kobold_exe = os.path.join(project_root, "koboldcpp", "koboldcpp.exe")
    model_path = os.path.join(project_root, "models", model_name)
    
    if not os.path.exists(kobold_exe):
        print(f"Error: KoboldCpp executable not found at {kobold_exe}")
        return

    if not os.path.exists(model_path):
        print(f"Warning: Model file not found at {model_path}. KoboldCpp might fail to start.")

    # Construct command
    cmd = [
        kobold_exe,
        "--model", model_path,
        "--port", "5001",
        "--gpulayers", str(gpu_layers)
    ]
    
    print(f"Starting KoboldCpp with command: {' '.join(cmd)}")
    
    # Launch in a new console window (Windows specific)
    try:
        if sys.platform == "win32":
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # For other platforms if needed
            subprocess.Popen(["x-terminal-emulator", "-e"] + cmd)
    except Exception as e:
        print(f"Failed to launch KoboldCpp: {e}")

if __name__ == "__main__":
    launch()
