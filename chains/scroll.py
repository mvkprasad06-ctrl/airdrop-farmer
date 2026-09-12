"""Scroll testnet actions."""
import random
import time

class ScrollFarmer:
    def __init__(self, w3_scroll, account, logger):
        self.w3 = w3_scroll
        self.account = account
        self.logger = logger
    
    def run_actions(self, count: int):
        actions = ['swap', 'mint', 'vote']
        for _ in range(count):
            action = random.choice(actions)
            self.logger.info(f'[Scroll] Simulated {action}')
            time.sleep(random.uniform(20, 40))