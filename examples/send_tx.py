# examples/send_tx.py

import requests
import json
import time
import os
import sys
from pathlib import Path
from importlib import util

# --- KOREKSI MUTLAK: Setup Impor dan Error Handling ---

# Ini memungkinkan Python menemukan modul 'src' saat dijalankan dengan 'python -m examples.send_tx'
# atau saat dijalankan dari folder root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)) 

try:
    # Mengimpor modul sebagai src.module (Absolute Import)
    from src.tx import Transaction
    from src.wallet import Wallet
    from src.utils import hash_data
except ImportError as e:
    print("\n\n❌ KESALAHAN FATAL: Gagal memuat modul inti.")
    print("------------------------------------------------------------------")
    print("PASTIKAN:")
    print("1. Anda menjalankan perintah: python -m examples.send_tx")
    print("2. Pustaka 'ecdsa' terinstal di VENV Anda (pip install -r requirements.txt)")
    print(f"Detail: {e}")
    print("------------------------------------------------------------------")
    sys.exit(1)

# ====================================================================
# 1. KONFIGURASI GLOBAL
# ====================================================================

SENDER_NAME = 'alice' 
RECIPIENT_NAME = 'bob'
NODE_URL = 'http://localhost:8001'
AMOUNT = 10.5 

# ====================================================================
# 2. MUAT KUNCI DARI FILE
# ====================================================================

# BASE_DIR HARUS DIKOREKSI AGAR TIDAK MENGANDUNG '\examples' DUA KALI
BASE_DIR = Path(__file__).resolve().parent.parent # Ini adalah C:\project\blockchain-lv2\

def load_key_from_file(wallet_name: str, key_type: str) -> str:
    """Fungsi pembantu untuk memuat kunci HEX dari file."""
    
    # KOREKSI: Menggunakan BASE_DIR dan joinpath untuk membangun path yang akurat.
    # BASE_DIR / 'examples' / 'alice_private.pem'
    file_path = BASE_DIR.joinpath('examples', f'{wallet_name}_{key_type}.pem')
    
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"\n❌ ERROR: File kunci '{file_path}' tidak ditemukan.")
        print("Silakan jalankan 'python -m examples.create_wallet' terlebih dahulu.")
        sys.exit(1)

# --- PEMANGGILAN FUNGSI DIMULAI DI SINI ---
alice_private_key = load_key_from_file(SENDER_NAME, 'private')
alice_public_key = load_key_from_file(SENDER_NAME, 'public')
bob_public_key = load_key_from_file(RECIPIENT_NAME, 'public')

# Inisialisasi Wallet untuk penandatanganan
alice_wallet = Wallet(private_key_hex=alice_private_key) # <--- Menggunakan KEYWORD YANG BENAR

print(f"Wallet '{SENDER_NAME}' dimuat. Siap mengirim {AMOUNT} koin ke '{RECIPIENT_NAME}'.")

# ====================================================================
# 3. BUAT & TANDATANGANI TRANSAKSI
# ====================================================================

tx = Transaction(
    sender=alice_public_key,
    recipient=bob_public_key,
    amount=AMOUNT,
    timestamp=time.time() 
)

# Tandatangani Transaksi (melalui objek Wallet)
tx.sign(alice_wallet)

# Verifikasi lokal (opsional, untuk debugging)
if tx.validate_tx():
    print("✅ Verifikasi lokal sukses!")
else:
    print("❌ Verifikasi lokal GAGAL! Ada masalah dengan kunci/signature.")
    sys.exit(1)

print("-" * 50)
print(f"TX ID: {tx.id[:15]}...")
print(f"Signature (HEX): {tx.signature[:30]}...")
print(f"Timestamp: {tx.timestamp}")
print("-" * 50)


# ====================================================================
# 4. KIRIM TRANSAKSI KE NODE
# ====================================================================

try:
    tx_payload = tx.model_dump() 
    
    response = requests.post(f'{NODE_URL}/transactions/new', json=tx_payload)
    response.raise_for_status() 
    
    print("\n🚀 Transaksi berhasil dikirim ke node:")
    print(json.dumps(response.json(), indent=2))
    
    print(f"\n✅ Transaksi sukses! Cek di {NODE_URL}/mempool")

except requests.exceptions.HTTPError as e:
    print(f"\n❌ Gagal mengirim transaksi (HTTP Error): {e}")
    try:
        error_detail = e.response.json()
        print("Detail Error dari Node:")
        print(json.dumps(error_detail, indent=2))
    except (json.JSONDecodeError, AttributeError):
        pass

except requests.exceptions.RequestException as e:
    print(f"\n❌ Gagal terhubung ke node di {NODE_URL}. Pastikan node berjalan.")
    print(f"Detail: {e}")

sys.exit(0)