# src/wallet.py

from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError
import binascii
from typing import Tuple
import time
import json 
# GANTI INI: from utils import hash_data
from .utils import hash_data # <--- KOREKSI: Gunakan relative import yang benar
import hashlib

class Wallet:
    """Mengelola kunci ECDSA dan penandatanganan menggunakan library ecdsa."""
    def __init__(self, private_key_hex: str = None):
        if private_key_hex:
            # Menggunakan string hex yang ada
            self._sk = SigningKey.from_string(binascii.unhexlify(private_key_hex), curve=SECP256k1)
        else:
            # Membuat kunci baru
            self._sk = SigningKey.generate(curve=SECP256k1)
        self._vk = self._sk.get_verifying_key()

    @property
    def private_key_hex(self) -> str:
        """Mengembalikan kunci privat dalam format HEX."""
        return binascii.hexlify(self._sk.to_string()).decode()

    @property
    def public_key_hex(self) -> str:
        """Mengembalikan kunci publik (digunakan sebagai alamat) dalam format HEX."""
        # Menghapus byte prefix (04) jika ada, tapi untuk kesederhanaan, kita gunakan versi to_string()
        return binascii.hexlify(self._vk.to_string()).decode()

    def sign(self, message_hash: str) -> str:
        """
        Menandatangani hash pesan (HEX string).
        Output: Signature dalam format HEX string.
        """
        message_bytes = binascii.unhexlify(message_hash)
        sig = self._sk.sign(message_bytes, hashfunc=hashlib.sha256)
        return binascii.hexlify(sig).decode()

    @staticmethod
    def verify(public_key_hex: str, message_hash: str, signature_hex: str) -> bool:
        """
        Memverifikasi signature (HEX) untuk hash pesan (HEX) dengan kunci publik (HEX).
        """
        try:
            vk = VerifyingKey.from_string(binascii.unhexlify(public_key_hex), curve=SECP256k1)
            sig_bytes = binascii.unhexlify(signature_hex)
            message_bytes = binascii.unhexlify(message_hash) # Message harus berupa hash bytes
            
            # Jika verifikasi berhasil, tidak ada exception yang dilempar
            vk.verify(sig_bytes, message_bytes, hashfunc=hashlib.sha256)
            return True
        except (BadSignatureError, Exception):
            return False

# --- Fungsi Pembantu (untuk digunakan oleh create_wallet.py) ---
def generate_key_pair() -> Tuple[str, str]:
    """
    Menghasilkan pasangan kunci privat dan publik baru (HEX).
    """
    w = Wallet()
    return w.private_key_hex, w.public_key_hex

def verify_signature(public_key_hex: str, data_to_verify_hash: str, signature_hex: str) -> bool:
    """Fungsi pembantu yang dipanggil oleh tx.py"""
    return Wallet.verify(public_key_hex, data_to_verify_hash, signature_hex)