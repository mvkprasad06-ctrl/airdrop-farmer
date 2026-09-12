"""Pure HTTP/web3.py Airdrop Farmer - No Browser, No Selenium"""
import os
import sys
import json
import time
import random
import logging
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.crypto import load_encrypted
from utils.telegram import TelegramNotifier
from utils.monitor import collect_stats
from utils.http_faucets import claim_all_faucets
from utils.web3_actions import Web3Actions
from web3 import Web3
import yaml

class Farmer:
    def __init__(self, config, password):
        self.config = config
        self.password = password
        self.wallets = []
        self.state = {'nonces': {}, 'last_run': {}}
        self.notifier = TelegramNotifier()
        self.setup_logging()
        self.load_wallets()
        self.load_state()
        self.init_web3()
        self.init_actions()
    
    def setup_logging(self):
        log_file = self.config['logging']['file'].format(date=datetime.now().strftime('%Y%m%d'))
        Path(log_file).parent.mkdir(exist_ok=True)
        logging.basicConfig(
            level=getattr(logging, self.config['logging']['level']),
            format='%(asctime)s | %(levelname)-8s | %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_wallets(self):
        wallet_file = self.config['wallets']['file']
        if not Path(wallet_file).exists():
            self.logger.error(f'Wallet file {wallet_file} not found. Run wallet_setup.py first.')
            sys.exit(1)
        self.wallets = load_encrypted(self.password, wallet_file)
        self.logger.info(f'Loaded {len(self.wallets)} wallets')
    
    def load_state(self):
        state_file = Path('state/state.json')
        if state_file.exists():
            with open(state_file) as f:
                self.state = json.load(f)
    
    def save_state(self):
        Path('state').mkdir(exist_ok=True)
        with open('state/state.json', 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def init_web3(self):
        rpcs = self.config['rpcs']
        self.w3 = {}
        for name, url in rpcs.items():
            try:
                w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 30}))
                if w3.is_connected():
                    self.w3[name] = w3
                    self.logger.info(f'RPC {name}: connected (block {w3.eth.block_number})')
                else:
                    self.logger.warning(f'RPC {name}: not connected')
            except Exception as e:
                self.logger.error(f'RPC {name} failed: {e}')
    
    def init_actions(self):
        self.actions = Web3Actions(self.w3, self.config, self.logger)
    
    def run_wallet(self, wallet: dict, action_count: int):
        wallet_id = wallet['id']
        address = wallet['address']
        private_key = wallet['private_key']
        self.logger.info(f'=== Wallet {wallet_id:02d} ({address[:8]}...) ===')
        
        try:
            # 1. Claim faucets via HTTP
            chains = ['sepolia', 'arbitrum_sepolia', 'optimism_sepolia', 'base_sepolia', 
                      'linea_sepolia', 'scroll_sepolia']
            faucet_results = claim_all_faucets(address, chains)
            for chain, success in faucet_results.items():
                self.logger.info(f'  Faucet {chain}: {"OK" if success else "FAIL"}')
            
            # 2. Execute chain actions via web3.py
            self.logger.info(f'  Running {action_count} chain actions...')
            for i in range(action_count):
                if not self.w3:
                    self.logger.warning('  No RPCs connected')
                    break
                chain_name = random.choice(list(self.w3.keys()))
                try:
                    self.actions.execute_random_action(chain_name, address, private_key)
                except Exception as e:
                    self.logger.error(f'  Action failed on {chain_name}: {e}')
                time.sleep(random.uniform(
                    self.config['delays']['min_action_delay'],
                    self.config['delays']['max_action_delay']
                ))
            
            self.logger.info(f'  Wallet {wallet_id:02d} complete')
            
        except Exception as e:
            self.logger.error(f'  Wallet {wallet_id:02d} error: {e}')
            self.notifier.alert('ERROR', f'Wallet {wallet_id} failed', str(e))
        finally:
            time.sleep(random.uniform(
                self.config['delays']['min_wallet_delay'],
                self.config['delays']['max_wallet_delay']
            ))
    
    def run(self, wallet_count: int = None, faucets_only: bool = False):
        wallets = self.wallets[:wallet_count] if wallet_count else self.wallets
        action_count = 0 if faucets_only else self.config['schedule']['cron_actions']
        
        self.notifier.alert('INFO', f'Farmer run started', f'{len(wallets)} wallets, {action_count} actions each')
        self.logger.info(f'Starting farmer run: {len(wallets)} wallets, {action_count} actions each')
        
        for wallet in wallets:
            self.run_wallet(wallet, action_count)
        
        self.save_state()
        
        stats = collect_stats()
        stats['wallets'] = len(wallets)
        self.notifier.daily_summary(stats)
        
        self.notifier.alert('INFO', 'Farmer run completed', f'{len(wallets)} wallets processed')
        self.logger.info('Run complete')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--wallets', type=int, help='Number of wallets to run')
    parser.add_argument('--test-run', action='store_true', help='Quick test with 1 wallet')
    parser.add_argument('--faucets-only', action='store_true', help='Only claim faucets')
    args = parser.parse_args()
    
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    
    password = os.environ.get('WALLET_PASSWORD')
    if not password:
        password = input('Wallet password: ')
    
    farmer = Farmer(config, password)
    
    if args.test_run:
        farmer.run(wallet_count=1)
    elif args.faucets_only:
        farmer.run(wallet_count=args.wallets, faucets_only=True)
    else:
        farmer.run(wallet_count=args.wallets)

if __name__ == '__main__':
    main()