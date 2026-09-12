"""Linea testnet actions."""
import random
import time

class LineaFarmer:
    def __init__(self, w3_linea, account, logger):
        self.w3 = w3_linea
        self.account = account
        self.logger = logger
    
    def run_actions(self, count: int):
        actions = ['swap', 'mint', 'deploy']
        for _ in range(count):
            action = random.choice(actions)
            self.logger.info(f'[Linea] Simulated {action}')
            time.sleep(random.uniform(20, 40))