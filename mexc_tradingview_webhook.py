import hmac
import hashlib
import time
import requests
from flask import Flask, request, jsonify

# === HIER DIREKT DEINE API-KEYS EINTRAGEN ===
API_KEY = "mx0vglME1m6DJMyJp0"
API_SECRET = "47bc0ec01bbc4bcd8895b589df35d2b1"
# ============================================

app = Flask(__name__)

def sign(payload):
    return hmac.new(API_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()

def place_order(side):
    url = "https://api.mexc.com/api/v3/order"
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": "BTCUSDT",
        "side": side.upper(),
        "type": "MARKET",
        "quantity": 0.001,  # Testgröße
        "timestamp": timestamp
    }
    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = sign(query)
    params["signature"] = signature
    headers = {"X-MEXC-APIKEY": API_KEY}
    resp = requests.post(url, params=params, headers=headers)
    return resp.json()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Alert empfangen:", data)
    if not data or "side" not in data:
        return jsonify({"error": "Kein 'side' in payload"}), 400

    side = data["side"]
    if side not in ["buy", "close"]:
        return jsonify({"error": "Unbekannte side"}), 400

    order_side = "BUY" if side == "buy" else "SELL"
    result = place_order(order_side)
    print("Order-Result:", result)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

