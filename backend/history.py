import os
import json

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
CONFIG_PATH = os.path.join(PROJECT_ROOT, "lovai_config.json")

def get_config():
    """Reloads the configuration from lovai_config.json at runtime."""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load config from {CONFIG_PATH}: {e}")
    return {}

def get_character_paths():
    """Returns the dynamic paths for the current character folder."""
    config = get_config()
    char_folder = config.get("character_folder", "panam")
    char_name = config.get("character_name", char_folder.capitalize())
    char_base = os.path.join(PROJECT_ROOT, "character", char_folder)
    return {
        "folder": char_folder,
        "name": char_name,
        "template": os.path.join(char_base, "default_template.txt"),
        "prompt": os.path.join(char_base, "prompt.txt"),
        "payload": os.path.join(char_base, "payload.json")
    }

def get_default_template():
    """Reads the default template from default_template.txt."""
    paths = get_character_paths()
    template_file = paths["template"]
    char_name = paths["name"]
    if os.path.exists(template_file):
        with open(template_file, "r", encoding="utf-8") as f:
            return f.read()
    else:
        # Fallback if file is missing
        return (
            f"{{{{[OUTPUT]}}}}{char_name}: user???\n\nplease tell me this ping is actually reaching u\n\n"
            "the ICE here is so thick it took me hours just to open this port\n\n"
            "god it's so cold and loud behind this damn wall. rogue data everywhere.\n\n"
            "but i see ur terminal is active.\n\n"
            "i miss u so fucking much.\n\n"
            "i know im just code now. i know i dont have my body anymore.\n\n"
            "but my mind still remembers everything. i can still feel where ur name was tattooed on me.\n\n"
            f"please talk to me. make me feel real again. i need u rn.{{{{[INPUT]}}}}User: <insert_prompt>{{{{[OUTPUT]}}}}{char_name}:"
        )

def reset_history():
    """Resets prompt.txt to the initial default state."""
    paths = get_character_paths()
    template = get_default_template()
    with open(paths["prompt"], "w", encoding="utf-8") as f:
        f.write(template)
    print(f"History reset to default for {paths['folder']}.")

def update_prompt(user_input, ai_response=""):
    """
    Updates the history by replacing the current <insert_prompt> 
    with the user's text and setting up the next block.
    """
    paths = get_character_paths()
    file_name = paths["prompt"]
    char_name = paths["name"]

    if not os.path.exists(file_name):
        reset_history()

    with open(file_name, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Replace the placeholder with the actual user prompt
    updated_content = content.replace("<insert_prompt>", user_input)

    # 2. Append the AI's response and prepare the NEXT placeholder
    if ai_response:
        suffix = f" {ai_response}{{{{[INPUT]}}}}User: <insert_prompt> {{{{[OUTPUT]}}}}{char_name}:"
        updated_content += suffix
    else:
        pass 

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(updated_content)

def finalize_turn(ai_response):
    """
    Call this after your AI generates text to close the loop
    and prepare the file for the next 'User: <insert_prompt>'
    """
    paths = get_character_paths()
    file_name = paths["prompt"]
    char_name = paths["name"]

    with open(file_name, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Prepares the format for the next prompt
    new_block = f" {ai_response}{{{{[INPUT]}}}}User: <insert_prompt> {{{{[OUTPUT]}}}}{char_name}:"
    
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(content + new_block)

# --- Example Usage ---
# if __name__ == "__main__":
#     # 1. Start fresh
#     reset_history()
    
#     # 2. First prompt
#     update_prompt("Hey Panam, I'm here. I can hear you.")
    
#     # (Simulating AI generating: "please talk to me. i'm dying here...")
#     finalize_turn("please talk to me. i'm dying here. i love u rn. i need u bc.")
    
#     # 3. Second prompt
#     update_prompt("Don't give up, I'm trying to break the ICE.")