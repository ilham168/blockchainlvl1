# src/app.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import os
import requests
from .wallet import generate_key_pair
from .node import Node
from .tx import Transaction
from .blockchain import Blockchain

import uvicorn
from dataclasses import asdict 

# Fungsi utilitas untuk konversi Block (Dataclass) ke Dict yang siap JSON
def block_to_dict(block):
    d = asdict(block)
    # Pastikan transaksi dikonversi dari Pydantic BaseModel ke Dict
    # Ini benar karena Transaction adalah Pydantic BaseModel
    d['transactions'] = [t.model_dump() for t in block.transactions] 
    return d
# -------------------------------
# Konfigurasi environment
# -------------------------------
PORT = int(os.environ.get("PORT", "8000"))
BOOTSTRAP = os.environ.get("BOOTSTRAP_PEERS", "")
bootstrap_peers = []

if BOOTSTRAP:
    for peer in BOOTSTRAP.split(","):
        peer = peer.strip()
        if not peer:
            continue
        # Tambahkan prefix http:// jika belum ada
        if not peer.startswith("http"):
            peer = f"http://{peer}"
        bootstrap_peers.append(peer)

# Inisialisasi node
NODE = Node(port=PORT, bootstrap_peers=bootstrap_peers)
app = FastAPI(title=f"Blockchain Node {PORT}")
from fastapi.middleware.cors import CORSMiddleware

# Setelah inisialisasi FastAPI
app = FastAPI(title=f"Blockchain Node {PORT}")

# Tambahkan ini ↓↓↓
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # untuk demo, izinkan semua origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -------------------------------
# Startup Event
# -------------------------------
@app.on_event("startup")
def startup_event():
    if bootstrap_peers:
        NODE.register_peers(bootstrap_peers)
    print(f"[Node {PORT}] Peers terdaftar: {NODE.peers}")

# -------------------------------
# Blockchain Endpoint
# -------------------------------
@app.get("/blocks")
def get_chain():
    # KOREKSI KRITIS: Menggunakan fungsi block_to_dict untuk menserialisasi Block
    return {
        "chain": [block_to_dict(b) for b in NODE.blockchain.chain], 
        "length": len(NODE.blockchain.chain)
    }

# -------------------------------
# Transaksi
# -------------------------------
@app.post("/transactions/new")
def new_transaction(tx_data: dict):
    """
    Tambahkan transaksi baru ke mempool.
    Jika mode DUMMY diaktifkan, maka skip validasi signature (untuk UI testing).
    """
    import os
    from fastapi import HTTPException

    # Cek apakah kita mengizinkan dummy mode
    ALLOW_DUMMY = os.environ.get("ALLOW_DUMMY_TX", "true").lower() == "true"

    try:
        tx = Transaction(**tx_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid transaction format: {str(e)}")

    # Jika bukan dummy mode → wajib validasi
    if not ALLOW_DUMMY:
        if not tx.validate_tx():
            raise HTTPException(status_code=400, detail="Transaction rejected (Invalid signature, duplicate, or insufficient funds)")
    else:
        print("⚠️ [DUMMY MODE] Validasi signature dilewati (testing UI).")

    NODE.mempool.add_transaction(tx)
    return {"message": "Transaction added to mempool", "tx_id": tx.id}


@app.get("/mempool")
def mempool_view():
    return {
        "mempool": [t.model_dump() for t in NODE.mempool.txs], # Menggunakan .txs
        "count": len(NODE.mempool.txs)
    }

# -------------------------------
# Mining
# -------------------------------
@app.post("/mine")
def mine(dummy: bool = False):
    """
    Tambahkan block baru ke chain.
    Jika dummy=True, node akan tetap memproses transaksi meskipun tidak valid.
    """
    try:
        # 🔹 Ambil semua transaksi dari mempool
        txs = NODE.mempool.all_transactions()

        if not txs:
            raise HTTPException(status_code=400, detail="Mempool kosong, tidak ada transaksi untuk ditambang.")

        # 🔹 Lakukan Proof of Work
        nonce, block_hash = NODE.blockchain.proof_of_work(
            txs, NODE.blockchain.last_block.hash
        )

        # 🔹 Buat block baru dan tambahkan ke chain
        new_block = NODE.blockchain.create_block(
            nonce=nonce,
            previous_hash=NODE.blockchain.last_block.hash,
            transactions=txs,
            miner_address=NODE.node_address
        )

        # 🔹 Hapus transaksi yang sudah ditambang (berdasarkan ID)
        NODE.mempool.remove_transactions([tx.id for tx in txs])

        # 🔹 Broadcast block ke node lain
        NODE.broadcast_block(new_block)

        return {"message": "New block forged", "block": new_block.__dict__}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mining failed: {e}")



# -------------------------------
# Node Management
# -------------------------------
@app.post("/nodes/register")
def register_nodes(payload: dict):
    nodes = payload.get("nodes", [])
    if not nodes:
        raise HTTPException(status_code=400, detail="No nodes provided")
    NODE.register_peers(nodes)
    return {"message": "Nodes registered", "total_nodes": len(NODE.peers)}

@app.get("/nodes")
def get_nodes():
    return {"nodes": NODE.peers}

# -------------------------------
# Receive Block
# -------------------------------
@app.post("/nodes/receive_block")
async def receive_block(payload: dict):
    try:
        from .blockchain import Block
        txs = [Transaction.model_validate(t) for t in payload.get("transactions", [])]
        block = Block(
            index=payload["index"],
            timestamp=payload.get("timestamp"),
            transactions=txs,
            nonce=payload["nonce"],
            previous_hash=payload["previous_hash"],
            difficulty=payload.get("difficulty", 3),
            hash=payload.get("hash", "")
        )
    except Exception as e:
        return JSONResponse({"message": "Invalid block payload", "error": str(e)}, status_code=400)

    last = NODE.blockchain.last_block
    if block.previous_hash == last.hash:
        if block.validate_block():
            NODE.blockchain.chain.append(block)
            # KOREKSI: Hapus transaksi non-coinbase dari mempool
            NODE.mempool.remove_transactions([t.id for t in block.transactions if t.sender != 'coinbase'])
            return {"message": "Block added"}
        else:
            return JSONResponse({"message": "Invalid block"}, status_code=400)
    else:
        return JSONResponse({
            "message": "Block does not link to current chain tip, consider resolving conflicts"
        }, status_code=409)
# -------------------------------
# Receive Transaction
# -------------------------------
@app.post("/nodes/receive_tx")
async def receive_tx(payload: dict):
    try:
        tx = Transaction.model_validate(payload)
    except Exception as e:
        return JSONResponse({"message": "Invalid tx payload", "error": str(e)}, status_code=400)

    # KOREKSI: Panggil mempool.add_transaction dengan objek blockchain untuk cek saldo
    added = NODE.mempool.add_transaction(tx, blockchain=NODE.blockchain)
    if not added:
        return JSONResponse({"message": "Tx duplicate, invalid signature, or insufficient funds"}, status_code=400)

    return {"message": "Tx accepted"}

# -------------------------------
# Resolve Conflicts
# -------------------------------
@app.post("/nodes/resolve")
def resolve():
    chains = []
    for peer in NODE.peers:
        try:
            r = requests.get(f"{peer}/blocks", timeout=3)
            if r.status_code == 200:
                data = r.json()
                chains.append(data.get("chain", []))
        except Exception:
            continue

    replaced = NODE.blockchain.resolve_conflicts(chains)
    if replaced:
        return {"message": "Our chain was replaced"}
    else:
        return {"message": "Our chain is authoritative"}
        
@app.get("/balance/{public_key}")
def get_balance(public_key: str):
    balance = NODE.blockchain.get_balance(public_key)
    return {"address": public_key, "balance": balance}
@app.get("/balance/{pubkey}")
def get_balance(pubkey: str):
    balance = NODE.blockchain.get_balance(pubkey)
    return {"balance": balance}

# -------------------------------
# Run Server
# -------------------------------
if __name__ == "__main__":
    uvicorn.run("src.app:app", host="0.0.0.0", port=PORT, reload=True)
