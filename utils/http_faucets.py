"""HTTP-based faucet claimers - no browser needed"""
import time
import random
import requests
from typing import Dict

FAUCET_ENDPOINTS = {
    'sepolia': [
        {'url': 'https://faucet.quicknode.com/ethereum/sepolia', 'method': 'POST', 'data_key': 'address'},
        {'url': 'https://www.alchemy.com/faucets/ethereum-sepolia', 'method': 'POST', 'data_key': 'address'},
    ],
    'arbitrum_sepolia': [
        {'url': 'https://faucet.quicknode.com/arbitrum/sepolia', 'method': 'POST', 'data_key': 'address'},
    ],
    'optimism_sepolia': [
        {'url': 'https://faucet.quicknode.com/optimism/sepolia', 'method': 'POST', 'data_key': 'address'},
    ],
    'base_sepolia': [
        {'url': 'https://faucet.quicknode.com/base/sepolia', 'method': 'POST', 'data_key': 'address'},
    ],
    'linea_sepolia': [
        {'url': 'https://faucet.linea.build', 'method': 'POST', 'data_key': 'address'},
    ],
    'scroll_sepolia': [
        {'url': 'https://faucet.scroll.io', 'method': 'POST', 'data_key': 'address'},
    ],
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

def claim_faucet(address: str, chain: str) -> bool:
    for endpoint in FAUCET_ENDPOINTS.get(chain, []):
        try:
            data = {endpoint['data_key']: address}
            response = requests.post(
                endpoint['url'],
                json=data,
                headers=HEADERS,
                timeout=30
            )
            if response.status_code in (200, 201):
                result = response.json() if response.content else {}
                if result.get('success') or result.get('txHash') or 'success' in str(result).lower():
                    return True
            time.sleep(random.uniform(2, 5))
        except Exception:
            continue
    return False

def claim_all_faucets(address: str, chains: list) -> Dict[str, bool]:
    results = {}
    for chain in chains:
        results[chain] = claim_faucet(address, chain)
        time.sleep(random.uniform(3, 8))
    return results