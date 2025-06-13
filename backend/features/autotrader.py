import threading
import time
import os
import yfinance as yf
from dotenv import load_dotenv
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Load environment variables
load_dotenv()
API_KEY = os.getenv("ALPACA_KEY") or os.getenv("API_KEY")
API_SECRET = os.getenv("ALPACA_SECRET") or os.getenv("API_SECRET")
PAPER = os.getenv("PAPER", "True").lower() == "true"

# Alpaca client
trading_client = TradingClient(API_KEY, API_SECRET, paper=PAPER)

# Global state
autotrading = False
trade_thread = None
profit_log = []

# Stocks to monitor
STOCK_POOL = [
    "AAPL", "NVDA", "MSFT", "AMD", "TSLA", "GOOGL", "META",
    "AMZN", "NFLX", "CRM", "JPM", "BA", "DIS", "XOM", "CVX"
]

# Get RSI and volume
def get_rsi_and_volume(ticker):
    try:
        df = yf.download(ticker, period="5d", interval="15m", progress=False)
        if df is None or df.empty or 'Close' not in df.columns:
            return None, None, None

        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_value = float(rsi.iloc[-1])
        volume_value = float(df['Volume'].rolling(14).mean().iloc[-1])
        last_close = float(df['Close'].iloc[-1])
        return rsi_value, volume_value, last_close
    except Exception as e:
        print(f"[ERROR] {ticker} indicators: {e}")
        return None, None, None

# Trade logic
def should_trade(ticker):
    rsi, volume, price = get_rsi_and_volume(ticker)
    if rsi is None:
        return None
    volume_str = str(int(volume)) if volume else "N/A"
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {ticker} | RSI: {rsi:.2f} | Volume: {volume_str}")
    if rsi < 35 and volume and volume > 500000:
        return "buy", price
    elif rsi > 70 and volume and volume > 500000:
        return "sell", price
    return None

# Submit live order
def place_order(symbol, qty, side, price):
    try:
        order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        trading_client.submit_order(order)
        log = {
            "time": datetime.now().isoformat(),
            "symbol": symbol,
            "side": side,
            "price": price,
            "qty": qty
        }
        profit_log.append(log)
        print(f"[TRADE] {side.upper()} {qty} {symbol} @ ${price}")
    except Exception as e:
        print(f"[ERROR] Trade failed for {symbol}: {e}")

# Core loop
def run_autotrading_loop():
    global autotrading
    print("[AUTOTRADER] Started.")
    while autotrading:
        for symbol in STOCK_POOL:
            decision = should_trade(symbol)
            if decision:
                side, price = decision
                place_order(symbol, 1, side, price)
        time.sleep(90)
    print("[AUTOTRADER] Stopped.")

# Start autotrading
def start_autotrading():
    global autotrading, trade_thread
    if autotrading:
        return "Autotrading is already running."
    autotrading = True
    trade_thread = threading.Thread(target=run_autotrading_loop, daemon=True)
    trade_thread.start()
    return "Autotrading started."

# Stop autotrading
def stop_autotrading():
    global autotrading
    autotrading = False
    return "Autotrading stopped."

# Check if trading
def is_trading():
    return autotrading

# Return trade logs
def get_logs():
    return profit_log
