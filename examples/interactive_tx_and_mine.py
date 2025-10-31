import requests
import time
import json

# =====================================================
# KONFIGURASI NODE
# =====================================================
NODE_URL = "http://localhost:8001"
SENDER = "node-8001"  # node miner, sudah punya saldo

# =====================================================
# FUNGSI BANTUAN
# =====================================================
def print_json(title, data):
    print(f"\n🔹 {title}")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def send_transaction(recipient, amount):
    tx_data = {
        "sender": SENDER,
        "recipient": recipient,
        "amount": amount,
        "timestamp": time.time(),
        "signature": "coinbase"  # dummy signature
    }

    print("\n🚀 Mengirim transaksi ke node...")
    res = requests.post(f"{NODE_URL}/transactions/new", json=tx_data)
    if res.status_code != 200:
        print(f"❌ Gagal kirim transaksi: {res.status_code}")
        print_json("Detail", res.json())
        return False
    print_json("✅ Transaksi berhasil dikirim", res.json())
    return True


def mine_block():
    print("\n⛏️  Menambang blok baru...")
    res = requests.post(f"{NODE_URL}/mine")
    if res.status_code != 200:
        print(f"❌ Gagal mining: {res.status_code}")
        print_json("Detail", res.json())
        return False
    print_json("✅ Blok baru berhasil ditambang", res.json())
    return True


def check_balance(address):
    print(f"\n💰 Mengecek saldo penerima: {address} ...")
    res = requests.get(f"{NODE_URL}/balance/{address}")
    if res.status_code == 200:
        print_json("Saldo", res.json())
    else:
        print(f"❌ Gagal cek saldo (HTTP {res.status_code})")


# =====================================================
# PROGRAM UTAMA (INTERAKTIF)
# =====================================================
print("⚜️  === Blockchain CLI - Transaksi & Mining === ⚜️\n")

recipient = input("Masukkan nama penerima / public key penerima: ").strip()
amount_str = input("Masukkan jumlah koin yang ingin dikirim: ").strip()

try:
    amount = float(amount_str)
except ValueError:
    print("❌ Jumlah koin tidak valid.")
    exit(1)

# 1️⃣ Kirim transaksi
if not send_transaction(recipient, amount):
    exit(1)

# 2️⃣ Tunggu sejenak sebelum mining
print("\n⏳ Menunggu 2 detik sebelum mining...")
time.sleep(2)

# 3️⃣ Mulai mining
if not mine_block():
    exit(1)

# 4️⃣ Cek saldo penerima
check_balance(recipient)

print("\n✅ Proses transaksi & mining selesai.\n")
