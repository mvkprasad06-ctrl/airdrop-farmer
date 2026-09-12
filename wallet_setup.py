"""Generate and encrypt wallets."""
import os
import sys
import csv
import json
from eth_account import Account
from utils.crypto import save_encrypted

Account.enable_unaudited_hdwallet_features()

def generate_wallets(count: int) -> list[dict]:
    wallets = []
    for i in range(count):
        acct = Account.create()
        wallets.append({
            'id': i + 1,
            'address': acct.address,
            'private_key': acct.key.hex(),
            'created': __import__('datetime').datetime.utcnow().isoformat()
        })
    return wallets

def export_for_rabby(wallets: list[dict], filepath: str):
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['#', 'Address', 'Private Key'])
        for w in wallets:
            writer.writerow([w['id'], w['address'], w['private_key']])

def print_paper_backup(wallets: list[dict]):
    print('\n' + '='*60)
    print('PAPER BACKUP — WRITE THESE DOWN NOW')
    print('='*60)
    for w in wallets:
        print(f'\nWallet {w["id"]:02d}: {w["address"]}')
        print(f'  Private Key: {w["private_key"]}')
    print('\n' + '='*60)
    print('STORE OFFLINE. NO SCREENSHOTS. NO CLOUD.')
    print('='*60 + '\n')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=10)
    parser.add_argument('--output', default='wallets.enc')
    parser.add_argument('--csv', default='wallets_import.csv')
    args = parser.parse_args()

    password = os.environ.get('WALLET_PASSWORD')
    if not password:
        password = input('Enter encryption password (memorize this): ')
        confirm = input('Confirm password: ')
        if password != confirm:
            print('Passwords do not match!')
            sys.exit(1)

    print(f'Generating {args.count} wallets...')
    wallets = generate_wallets(args.count)
    
    print(f'Encrypting to {args.output}...')
    save_encrypted(wallets, password, args.output)
    
    print(f'Exporting CSV for Rabby to {args.csv}...')
    export_for_rabby(wallets, args.csv)
    
    print_paper_backup(wallets)
    print(f'Done. {args.count} wallets created.')
    print(f'Import {args.csv} into Rabby (Settings > Import > CSV)')