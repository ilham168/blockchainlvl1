import requests
import time
import json

NODE_URL = "http://localhost:8001"
SENDER = "node-8001"  # alamat miner kamu
RECIPIENT = "bob"     # ganti ini dengan public key Bob (atau string unik)
AMOUNT = 25.0

tx_data = {
    "sender": SENDER,
    "recipient": RECIPIENT,
    "amount": AMOUNT,
    "timestamp": time.time(),
    "signature": "coinbase"  # dummy signature
}

print("🚀 Mengirim transaksi dari node-8001 ke Bob...")
response = requests.post(f"{NODE_URL}/transactions/new", json=tx_data)

print("\nStatus:", response.status_code)
print("Response:")
print(json.dumps(response.json(), indent=2))
