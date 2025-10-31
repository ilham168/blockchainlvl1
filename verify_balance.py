# verify_balance.py
import sys
import os
import time

# --- KOREKSI: MENGGUNAKAN ABSOLUTE IMPORT DARI ROOT ---
# Baris ini menambahkan folder induk (blockchain-lv2) ke path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    # Import modul sebagai src.module
    from src.blockchain import Blockchain
    from src.tx import Transaction
    from src.wallet import Wallet, generate_key_pair
    from src.utils import hash_data
    from src.config import COINBASE_AMOUNT
except ImportError as e:
    print(f"Error mengimpor modul: {e}")
    print("Pastikan Anda menjalankan skrip dari folder utama (blockchain-lv2) dan semua file src/ sudah benar.")
    sys.exit(1)

# ====================================================================
# PENTING: GANTI DENGAN KUNCI PUBLIK DAN PRIVATE KEY DARI FILE ANDA
# Ambil konten HEX string dari alice_public.pem, alice_private.pem, dan bob_public.pem
# ====================================================================

# Kunci publik Alice dan Bob yang sudah Anda buat
ALICE_PUBLIC_KEY_HEX = "PASTE_ALICE_PUBLIC_KEY_HEX_HERE"
ALICE_PRIVATE_KEY_HEX = "PASTE_ALICE_PRIVATE_KEY_HEX_HERE"
BOB_PUBLIC_KEY_HEX = "PASTE_BOB_PUBLIC_KEY_HEX_HERE"

MINER_ADDRESS = "node-8001"
TRANSACTION_AMOUNT = 10.5

# ====================================================================
# 1. SETUP CHAIN & MINE BLOCK #2 (Reward)
# ====================================================================

bc = Blockchain() # Chain dimulai dengan Genesis Block (#1)
alice_wallet = Wallet(private_key_hex=ALICE_PRIVATE_KEY_HEX)

print("-" * 50)
print(f"STATUS AWAL (Setelah Genesis Block #1): Chain Length = {len(bc.chain)}")
print(f"Saldo Alice: {bc.get_balance(ALICE_PUBLIC_KEY_HEX):.2f} koin")
print(f"Saldo Miner ({MINER_ADDRESS}): {bc.get_balance(MINER_ADDRESS):.2f} koin")
print("-" * 50)


# --- Tindakan 1: Mine Block #2 (Coinbase untuk Miner) ---
print(">> MENAMBANG BLOCK #2 (Hanya Coinbase)...")
nonce2, hash2 = bc.proof_of_work([], bc.last_block.hash)
block2 = bc.create_block(
    nonce=nonce2,
    previous_hash=bc.last_block.hash,
    transactions=[],
    miner_address=MINER_ADDRESS
)
print(f"Block #2 Forged: Hash={block2.hash[:10]}...")
print(f"Saldo Miner setelah Block #2: {bc.get_balance(MINER_ADDRESS):.2f} koin")


# ====================================================================
# 2. BUAT & TANDATANGANI TRANSAKSI ALICE
# ====================================================================

print("\n>> MEMBUAT TRANSAKSI ALICE -> BOB (10.5 koin)...")
# Membuat objek Transaction
tx = Transaction(
    sender=ALICE_PUBLIC_KEY_HEX,
    recipient=BOB_PUBLIC_KEY_HEX,
    amount=TRANSACTION_AMOUNT,
    timestamp=time.time()
)
# Menandatangani dan menghitung ID
tx.sign(alice_wallet) 

if not tx.validate_tx():
    print("FATAL ERROR: Transaksi Alice gagal validasi!")
    sys.exit(1)
print(f"Transaksi Alice berhasil ditandatangani. TX ID: {tx.id[:10]}...")


# --- Tindakan 2: Mine Block #3 (Termasuk Transaksi Alice) ---
print("\n>> MENAMBANG BLOCK #3 (Termasuk Transaksi Alice)...")
txs_to_mine = [tx] # Transaksi yang akan dimasukkan ke blok
nonce3, hash3 = bc.proof_of_work(txs_to_mine, bc.last_block.hash)

block3 = bc.create_block(
    nonce=nonce3,
    previous_hash=bc.last_block.hash,
    transactions=txs_to_mine,
    miner_address=MINER_ADDRESS
)
print(f"Block #3 Forged: Hash={block3.hash[:10]}...")


# ====================================================================
# 3. VERIFIKASI SALDO AKHIR
# ====================================================================
print("\n" + "=" * 50)
print("HASIL AKHIR VERIFIKASI SALDO (Setelah Block #3)")
print("=" * 50)

final_miner_balance = bc.get_balance(MINER_ADDRESS)
final_alice_balance = bc.get_balance(ALICE_PUBLIC_KEY_HEX)
final_bob_balance = bc.get_balance(BOB_PUBLIC_KEY_HEX)

# Miner mendapat reward Block #2 dan Block #3
EXPECTED_MINER = COINBASE_AMOUNT * 2
# Alice tidak punya saldo awal, jadi dia akan negatif (hutang)
EXPECTED_ALICE = -TRANSACTION_AMOUNT
# Bob menerima 10.5
EXPECTED_BOB = TRANSACTION_AMOUNT

print(f"1. Miner ({MINER_ADDRESS})")
print(f"   Diharapkan: {EXPECTED_MINER:.2f} koin (50.0 + 50.0)")
print(f"   Aktual: {final_miner_balance:.2f} koin")
assert final_miner_balance == EXPECTED_MINER

print("\n2. Alice (Pengirim)")
print(f"   Diharapkan: {EXPECTED_ALICE:.2f} koin (0.0 - 10.5)")
print(f"   Aktual: {final_alice_balance:.2f} koin")
assert final_alice_balance == EXPECTED_ALICE

print("\n3. Bob (Penerima)")
print(f"   Diharapkan: {EXPECTED_BOB:.2f} koin (+10.5)")
print(f"   Aktual: {final_bob_balance:.2f} koin")
assert final_bob_balance == EXPECTED_BOB

print("\n✅ Verifikasi Saldo Selesai. Saldo sesuai dengan yang diharapkan.")