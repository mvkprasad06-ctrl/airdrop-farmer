"""Hyperliquid testnet actions."""
import random
import time

class HyperliquidFarmer:
    def __init__(self, w3_hl, account, logger):
        self.w3 = w3_hl
        self.account = account
        self.logger = logger
    
    def run_actions(self, count: int):
        actions = ['trade', 'lp', 'refer']
        for _ in range(count):
            action = random.choice(actions)
            self.logger.info(f'[Hyperliquid] Simulated {action}')
            time.sleep(random.uniform(30, 60))