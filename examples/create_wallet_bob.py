# examples/create_wallet_bob.py

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.wallet import generate_key_pair

wallet_name = 'bob'
output_dir = os.path.dirname(__file__)

priv, pub = generate_key_pair()

with open(os.path.join(output_dir, f'{wallet_name}_private.pem'), 'w') as f:
    f.write(priv.strip())
with open(os.path.join(output_dir, f'{wallet_name}_public.pem'), 'w') as f:
    f.write(pub.strip())

print(f"✅ Wallet '{wallet_name}' created in folder: {output_dir}")
