import os
import json
import requests
from backend.features.websearch import search_web
from backend.features.autotrader import start_autotrading, stop_autotrading, is_trading

# ========== Memory Path ==========
MEMORY_PATH = os.path.join(os.path.dirname(__file__), "core", "memory.json")

def load_memory():
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "r") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_PATH, "w") as f:
        json.dump(data, f, indent=4)

# ========== Offline Mistral LLM ==========
def ask_mistral(prompt: str) -> str:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False}
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        return "[Error] Mistral API did not return a valid response."
    except Exception as e:
        return f"[Error] Unable to reach Mistral: {e}"

# ========== Main Command Handler ==========
def handle_command(user_input: str) -> str:
    command = user_input.strip().lower()
    memory = load_memory()

    # Save memory
    if command.startswith("remember:"):
        try:
            key_value = user_input.split("remember:")[1].strip()
            key, value = key_value.split(" is ")
            memory[key.strip()] = value.strip()
            save_memory(memory)
            return f"Got it. I’ll remember that {key.strip()} is {value.strip()}."
        except:
            return "Format it like: remember: my birthday is August 29"

    # Recall memory
    elif command.startswith("recall:"):
        key = user_input.split("recall:")[1].strip()
        return memory.get(key, "I don't remember anything about that.")

    # Autonomous trading controls
    elif command == "start trading":
        return start_autotrading()

    elif command == "stop trading":
        return stop_autotrading()

    elif command == "status":
        return "Autotrading is active." if is_trading() else "Autotrading is off."

    # Identity responses
    elif command == "hello":
        return "Hello Felipe!"

    elif command == "who are you":
        return "I’m JARVIS, your personal AI assistant."

    elif command in {"who made you", "who created you"}:
        return "I was created by Felipe Ruiz — my one and only creator."

    elif command in {"who’s your owner", "who is your owner"}:
        return "Felipe Ruiz is my owner. I serve him only."

    elif command in {"what is your purpose", "why do you exist"}:
        return "My purpose is to assist Felipe Ruiz in becoming unstoppable."

    # Fallback → Mistral then Web
    else:
        response = ask_mistral(user_input)
        if response.lower().startswith("i’m still learning") or len(response.strip()) < 10:
            return search_web(user_input)
        return response
