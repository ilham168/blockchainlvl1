# examples/create_wallet.py (Final Fix)

import sys
import os

# Tambahkan direktori induk agar bisa import src.wallet
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.wallet import generate_key_pair

# Buat pasangan kunci
private_key, public_key = generate_key_pair()

# Tentukan folder output (selalu di folder examples)
wallet_name = 'alice'
output_dir = os.path.dirname(__file__)

private_path = os.path.join(output_dir, f'{wallet_name}_private.pem')
public_path = os.path.join(output_dir, f'{wallet_name}_public.pem')

# Simpan file
with open(private_path, 'w') as f:
    f.write(private_key.strip())

with open(public_path, 'w') as f:
    f.write(public_key.strip())

print(f"✅ Wallet '{wallet_name}' created in folder: {output_dir}")
print(f"- {private_path}")
print(f"- {public_path}")
