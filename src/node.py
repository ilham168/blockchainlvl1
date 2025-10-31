# src/node.py
import os
import requests
from typing import List, Any
from dataclasses import asdict
from .tx import Mempool, Transaction
from .blockchain import Blockchain
from .config import NETWORK_TIMEOUT

# fallback jika config tidak menyediakan constant (safety)
try:
    NETWORK_TIMEOUT = int(NETWORK_TIMEOUT)
except Exception:
    NETWORK_TIMEOUT = 3

class Node:
    def __init__(self, port: int, bootstrap_peers: List[str] = None):
        self.port = port
        # normalize peers to list of stripped urls (no trailing slash)
        self.peers = []
        if bootstrap_peers:
            for p in bootstrap_peers:
                norm = self._normalize_peer_url(p)
                if norm and norm not in self.peers and norm != self.self_url():
                    self.peers.append(norm)

        self.mempool = Mempool()
        self.blockchain = Blockchain()
        self.node_address = f"node-{self.port}"  # digunakan juga sebagai alamat miner

    # -------------------------
    # Helper utilities
    # -------------------------
    def _normalize_peer_url(self, peer: str) -> str:
        """Normalize peer string to full http://... form without trailing slash."""
        if not peer:
            return ""
        peer = peer.strip()
        if not peer:
            return ""
        if not peer.startswith("http://") and not peer.startswith("https://"):
            peer = f"http://{peer}"
        return peer.rstrip("/")

    # -----------------------------------
    # Peer management
    # -----------------------------------
    def register_peers(self, peers: List[str]):
        """Add a list of peers (strings). Accepts 'host:port' or full URL."""
        for p in peers:
            norm = self._normalize_peer_url(p)
            if norm and norm not in self.peers and norm != self.self_url():
                self.peers.append(norm)
        print(f"[Node] Peers after register: {self.peers}")

    def get_peers(self):
        return list(self.peers)

    def self_url(self) -> str:
        hostname = os.environ.get("HOSTNAME", f"node{self.port}")
        return f"http://{hostname}:{self.port}"

    # -----------------------------------
    # Broadcast transactions & blocks
    # -----------------------------------
    def broadcast_tx(self, tx: Transaction):
        """Broadcast a Transaction to all peers (POST /nodes/receive_tx)."""
        # serialize transaction to plain dict
        try:
            payload = tx.model_dump() if hasattr(tx, "model_dump") else asdict(tx)
        except Exception:
            # fallback generic
            payload = {
                "id": getattr(tx, "id", None),
                "sender": getattr(tx, "sender", None),
                "recipient": getattr(tx, "recipient", None),
                "amount": getattr(tx, "amount", None),
                "timestamp": getattr(tx, "timestamp", None),
                "signature": getattr(tx, "signature", None),
            }

        for peer in list(self.peers):
            try:
                url = f"{peer}/nodes/receive_tx"
                requests.post(url, json=payload, timeout=NETWORK_TIMEOUT)
            except Exception as e:
                print(f"[Broadcast TX] Gagal kirim ke {peer}: {e}")

    def broadcast_block(self, block: Any):
        """
        Kirim block baru ke semua node yang terdaftar agar mereka bisa memvalidasi dan menambahkannya.
        Endpoint di node target: POST /nodes/receive_block
        """
        # Build JSON-serializable payload
        payload = {
            "index": getattr(block, "index", None),
            "timestamp": getattr(block, "timestamp", None),
            "transactions": [
                (t.model_dump() if hasattr(t, "model_dump") else
                 (t.__dict__ if hasattr(t, "__dict__") else t))
                for t in getattr(block, "transactions", [])
            ],
            "nonce": getattr(block, "nonce", None),
            "previous_hash": getattr(block, "previous_hash", None),
            "difficulty": getattr(block, "difficulty", None),
            "hash": getattr(block, "hash", "")
        }

        for peer in list(self.peers):
            try:
                url = f"{peer}/nodes/receive_block"
                response = requests.post(url, json=payload, timeout=NETWORK_TIMEOUT)
                if response.status_code == 200:
                    print(f"✅ Block dikirim ke peer: {peer}")
                else:
                    print(f"⚠️ Peer {peer} menolak block (HTTP {response.status_code}) - {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Gagal kirim block ke {peer}: {e}")
