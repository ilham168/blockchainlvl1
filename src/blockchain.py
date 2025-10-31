from typing import List, Dict, Any, Optional, Tuple
import time
from dataclasses import dataclass
from .utils import hash_data, is_valid_proof
from .tx import Transaction, Mempool
from .config import DIFFICULTY, COINBASE_AMOUNT


@dataclass
class Block:
    index: int
    transactions: List[Transaction]
    nonce: int
    previous_hash: str
    difficulty: int
    timestamp: float = None
    hash: str = ""

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def calculate_hash(self) -> str:
        data = {
            "index": self.index,
            "transactions": [t.model_dump() for t in self.transactions],
            "nonce": self.nonce,
            "previous_hash": self.previous_hash,
            "difficulty": self.difficulty,
            "timestamp": self.timestamp,
        }
        return hash_data(data)

    def validate_block(self) -> bool:
        # Validasi hash block
        if self.hash != self.calculate_hash():
            return False
        # Validasi PoW
        if not is_valid_proof(self.hash, self.difficulty):
            return False
        # Validasi transaksi (skip coinbase)
        for tx in self.transactions[1:]:
            if not tx.validate_tx():
                return False
        return True


class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.mempool = Mempool()  # Tambahkan mempool agar konsisten dengan node
        self.create_genesis_block()

    def create_genesis_block(self):
        """Buat genesis block yang sah."""
        nonce, genesis_hash = self.proof_of_work([], '1', index_override=1)
        genesis = Block(
            index=1,
            transactions=[],
            nonce=nonce,
            previous_hash='1',
            difficulty=DIFFICULTY,
            hash=genesis_hash,
        )
        self.chain.append(genesis)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    # ===============================
    # 💠 Proof of Work
    # ===============================
    def proof_of_work(
        self,
        transactions: List[Transaction],
        previous_hash: str,
        index_override: Optional[int] = None,
    ) -> Tuple[int, str]:
        nonce = 0
        index = index_override if index_override is not None else len(self.chain) + 1
        base_data = {
            "index": index,
            "transactions": [t.model_dump() for t in transactions],
            "previous_hash": previous_hash,
            "difficulty": DIFFICULTY,
        }

        while True:
            d = dict(base_data)
            d["nonce"] = nonce
            d["timestamp"] = 0
            current_hash = hash_data(d)
            if is_valid_proof(current_hash, DIFFICULTY):
                return nonce, current_hash
            nonce += 1

    # ===============================
    # 💰 Mining Block
    # ===============================
    def mine_block(self, miner_address: str, allow_dummy: bool = False) -> Block:
        """
        Proses mining block baru.
        Jika allow_dummy=True, transaksi tidak divalidasi agar bisa uji dari dashboard.
        """
        if not self.mempool.transactions:
            raise ValueError("Mempool kosong — tidak ada transaksi untuk ditambang.")

        # Pilih transaksi valid atau dummy
        valid_txs = [
            tx for tx in self.mempool.transactions
            if allow_dummy or tx.validate_tx()
        ]

        if not valid_txs:
            raise ValueError("Tidak ada transaksi valid untuk ditambang.")

        # Tambahkan coinbase (reward)
        coinbase_tx = Transaction(
            sender="coinbase",
            recipient=miner_address,
            amount=COINBASE_AMOUNT,
            timestamp=time.time(),
            signature="coinbase",
        )
        coinbase_tx.id = coinbase_tx.calculate_id()
        all_txs = [coinbase_tx] + valid_txs

        nonce, _ = self.proof_of_work(all_txs, self.last_block.hash)
        new_block = Block(
            index=len(self.chain) + 1,
            transactions=all_txs,
            nonce=nonce,
            previous_hash=self.last_block.hash,
            difficulty=DIFFICULTY,
        )

        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

        # Bersihkan mempool setelah mining sukses
        self.mempool.transactions.clear()

        return new_block

    # ===============================
    # 🔗 Validasi & Sinkronisasi Chain
    # ===============================
    def is_valid_chain(self, chain: List[Block]) -> bool:
        if not chain:
            return False
        for i in range(1, len(chain)):
            block = chain[i]
            prev = chain[i - 1]
            if block.previous_hash != prev.hash:
                return False
            if not block.validate_block():
                return False
        return True

    def resolve_conflicts(self, peers_chains: List[List[Dict[str, Any]]]) -> bool:
        new_chain = None
        max_length = len(self.chain)

        for chain_data in peers_chains:
            try:
                candidate = []
                for b in chain_data:
                    txs = [Transaction(**t) for t in b.get("transactions", [])]
                    blk = Block(
                        index=b["index"],
                        transactions=txs,
                        nonce=b["nonce"],
                        previous_hash=b["previous_hash"],
                        difficulty=b.get("difficulty", DIFFICULTY),
                        timestamp=b.get("timestamp", time.time()),
                        hash=b.get("hash", ""),
                    )
                    candidate.append(blk)
            except Exception:
                continue

            if len(candidate) > max_length and self.is_valid_chain(candidate):
                max_length = len(candidate)
                new_chain = candidate

        if new_chain:
            self.chain = new_chain
            return True
        return False

    # ===============================
    # 💵 Cek Saldo
    # ===============================
    def get_balance(self, public_key: str) -> float:
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == public_key:
                    balance -= tx.amount
                if tx.recipient == public_key:
                    balance += tx.amount
        return balance
