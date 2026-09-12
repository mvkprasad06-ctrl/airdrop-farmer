"""LayerZero testnet actions."""
import random
import time
from web3 import Web3
from eth_account import Account

class LayerZeroFarmer:
    def __init__(self, w3_sepolia, w3_arb, w3_opt, account, logger):
        self.w3 = {'sepolia': w3_sepolia, 'arbitrum': w3_arb, 'optimism': w3_opt}
        self.account = account
        self.logger = logger
    
    def run_actions(self, count: int):
        chains = list(self.w3.keys())
        for _ in range(count):
            src = random.choice(chains)
            dst = random.choice([c for c in chains if c != src])
            self.logger.info(f'[LZ] Simulated bridge {src} -> {dst}')
            time.sleep(random.uniform(30, 60))