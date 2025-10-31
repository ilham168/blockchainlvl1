# src/tx.py

from pydantic import BaseModel
from typing import Optional, List, Any # Import Any untuk tipe Wallet
import time
from .utils import hash_data
# HAPUS: from .wallet import Wallet (Karena akan menyebabkan circular dependency)

class Transaction(BaseModel):
    id: Optional[str] = None
    sender: str
    recipient: str
    amount: float
    timestamp: float = None
    signature: Optional[str] = None

    def __init__(self, **data):
        if "timestamp" not in data or data.get("timestamp") is None:
            data["timestamp"] = time.time()
        super().__init__(**data)
        if self.id is None:
            self.id = self.calculate_id()

    def calculate_id(self) -> str:
        # ID adalah hash dari konten transaksi (tanpa signature/id)
        tx_dict = {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp,
        }
        return hash_data(tx_dict)

    # FUNGSI BARU UNTUK KONSISTENSI HASH
    def get_signing_hash(self) -> str: # <--- KOREKSI: Fungsi pembantu baru
        # Hash data yang digunakan untuk ditandatangani, sama dengan ID
        return self.calculate_id() 

    def sign(self, wallet: Any): # Any untuk menghindari circular import
        # Payload yang akan ditandatangani adalah hash-nya (HEX string)
        payload_hash = self.get_signing_hash() # <--- KOREKSI: Tandatangani HASH
        self.signature = wallet.sign(payload_hash)
        self.id = self.calculate_id() # Hitung ID final setelah tanda tangan

    def validate_tx(self) -> bool:
        from .wallet import verify_signature # <--- KOREKSI: Import lokal untuk circular dependency
        
        # Coinbase transactions have signature == 'coinbase'
        if self.sender == 'coinbase':
            return True
        if not self.signature:
            return False
        
        # Dapatkan hash yang sama yang digunakan saat penandatanganan
        payload_hash = self.get_signing_hash() # <--- KOREKSI: Verifikasi HASH
        
        # public_key_hex, data_to_verify_hash (HEX), signature_hex (HEX)
        return verify_signature(self.sender, payload_hash, self.signature)


class Mempool:
    def __init__(self):
        self.txs: List[Transaction] = []

    def add_transaction(self, tx: Transaction, blockchain=None) -> bool:
        # Validate signature
        if not tx.validate_tx():
            return False

        # Optional: check balance (simple account model)
        if blockchain:
            sender_balance = blockchain.get_balance(tx.sender)
            # Also account pending outgoing txs in mempool
            pending_out = sum(t.amount for t in self.txs if t.sender == tx.sender)
            if sender_balance - pending_out < tx.amount:
                return False

        # Prevent duplicates
        if any(existing.id == tx.id for existing in self.txs):
            return False

        self.txs.append(tx)
        return True

    def get_transactions_for_block(self, limit: int = 100) -> List[Transaction]:
        # Return up to `limit` transactions (excluding coinbase)
        return [tx for tx in self.txs][:limit]

    def remove_transactions(self, tx_ids: List[str]):
        self.txs = [tx for tx in self.txs if tx.id not in tx_ids]
    
    def all_transactions(self) -> List[Transaction]:
        return self.txs