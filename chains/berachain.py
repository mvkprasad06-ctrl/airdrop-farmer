"""Berachain testnet actions."""
import random
import time

class BerachainFarmer:
    def __init__(self, w3_bera, account, logger):
        self.w3 = w3_bera
        self.account = account
        self.logger = logger
    
    def run_actions(self, count: int):
        actions = ['swap', 'lp', 'delegate']
        for _ in range(count):
            action = random.choice(actions)
            self.logger.info(f'[Berachain] Simulated {action}')
            time.sleep(random.uniform(30, 60))