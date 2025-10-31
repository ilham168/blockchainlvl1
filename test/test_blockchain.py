# test_blockchain.py

import config
config.DIFFICULTY = 1  # buat tes lebih cepat

# KOREKSI: Impor semua yang dibutuhkan dan ganti nama fungsi yang salah
from src.wallet import generate_key_pair, Wallet 
from src.tx import Transaction, Mempool
from src.blockchain import Blockchain

# Fungsi pembantu untuk tes (Menggantikan tx.sign(priv) lama)
def sign_tx(tx: Transaction, private_key_hex: str):
    wallet = Wallet(private_key_hex=private_key_hex)
    tx.sign(wallet)

def test_wallet_and_tx_sign_verify():
    priv, pub = generate_key_pair() # <--- KOREKSI: Gunakan generate_key_pair
    addr = pub # <--- KOREKSI: Kunci publik digunakan sebagai alamat (Ganti pubkey_to_address(pub))
    
    tx = Transaction(sender=pub, recipient=addr, amount=10.0)
    sign_tx(tx, priv) # <--- KOREKSI: Gunakan fungsi pembantu
    
    assert tx.signature is not None
    assert tx.validate_tx()
    assert tx.id is not None

def test_mempool_add_and_remove():
    mp = Mempool()
    priv, pub = generate_key_pair() # <--- KOREKSI
    addr = pub # <--- KOREKSI
    
    tx = Transaction(sender=pub, recipient=addr, amount=5.0)
    sign_tx(tx, priv) # <--- KOREKSI
    
    added = mp.add_transaction(tx)
    assert added
    assert len(mp.all_transactions()) == 1
    mp.remove_transactions([tx.id])
    assert len(mp.all_transactions()) == 0

def test_mine_block_and_chain_properties():
    bc = Blockchain()
    # create a simple coinbase-only mining: simulate tx list empty
    txs = []
    nonce, h = bc.proof_of_work(transactions=txs, previous_hash=bc.last_block.hash)
    block = bc.create_block(nonce=nonce, previous_hash=bc.last_block.hash, transactions=txs, miner_address="miner-1")
    assert block.validate_block()
    assert len(bc.chain) == 2
    # check coinbase reward effect
    balance = bc.get_balance("miner-1")
    assert balance == 50.0
