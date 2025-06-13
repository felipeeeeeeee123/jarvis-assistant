from fastapi import FastAPI
from backend.command_handler import handle_command
from backend.features.autotrader import start_autotrading, stop_autotrading, is_trading, get_logs

import threading

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "JARVIS is running", "autotrading": is_trading()}

@app.get("/autotrade/start")
def start_trading():
    return {"message": start_autotrading()}

@app.get("/autotrade/stop")
def stop_trading():
    return {"message": stop_autotrading()}

@app.get("/autotrade/status")
def check_status():
    return {
        "active": is_trading(),
        "log_size": len(get_logs())
    }

@app.get("/autotrade/logs")
def get_trade_log():
    return get_logs()

def run_cli():
    print("JARVIS Assistant (CLI Mode). Type 'exit' to quit.")
    while True:
        try:
            user_input = input(">>> ")
            if user_input.lower() in {"exit", "quit"}:
                print("Exiting CLI...")
                break
            response = handle_command(user_input)
            print(response)
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    run_cli()
