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
from utils.browser import create_driver, get_profile_dir
from utils.faucets import claim_all_faucets
from utils.telegram import TelegramNotifier
from utils.monitor import collect_stats
import yaml

# Chain modules
from chains.layerzero import LayerZeroFarmer
from chains.linea import LineaFarmer
from chains.scroll import ScrollFarmer
from chains.hyperliquid import HyperliquidFarmer
from chains.berachain import BerachainFarmer
from web3 import Web3
from eth_account import Account

class Farmer:
    def __init__(self, config, password, headless=True):
        self.config = config
        self.password = password
        self.headless = headless
        self.wallets = []
        self.state = {'nonces': {}, 'last_run': {}}
        self.notifier = TelegramNotifier()
        self.setup_logging()
        self.load_wallets()
        self.load_state()
        self.init_web3()
        self.init_chain_farmers()
    
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
                self.w3[name] = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 30}))
                if self.w3[name].is_connected():
                    self.logger.info(f'RPC {name}: connected (block {self.w3[name].eth.block_number})')
                else:
                    self.logger.warning(f'RPC {name}: not connected')
            except Exception as e:
                self.logger.error(f'RPC {name} failed: {e}')
                self.w3[name] = None
    
    def init_chain_farmers(self):
        # Only init chains with working RPCs
        self.chain_farmers = {}
        if self.w3.get('sepolia') and self.w3.get('arbitrum_sepolia') and self.w3.get('optimism_sepolia'):
            self.chain_farmers['layerzero'] = LayerZeroFarmer(
                self.w3['sepolia'], self.w3['arbitrum_sepolia'], self.w3['optimism_sepolia'],
                self.wallets[0], self.logger
            )
        if self.w3.get('linea_sepolia'):
            self.chain_farmers['linea'] = LineaFarmer(self.w3['linea_sepolia'], self.wallets[0], self.logger)
        if self.w3.get('scroll_sepolia'):
            self.chain_farmers['scroll'] = ScrollFarmer(self.w3['scroll_sepolia'], self.wallets[0], self.logger)
        if self.w3.get('hyperliquid_testnet'):
            self.chain_farmers['hyperliquid'] = HyperliquidFarmer(self.w3['hyperliquid_testnet'], self.wallets[0], self.logger)
        if self.w3.get('berachain_artio'):
            self.chain_farmers['berachain'] = BerachainFarmer(self.w3['berachain_artio'], self.wallets[0], self.logger)
        
        self.logger.info(f'Initialized chain farmers: {list(self.chain_farmers.keys())}')
    
    def get_driver(self, wallet_id: int):
        profile_dir = get_profile_dir(self.config['browser']['user_data_dir'], wallet_id)
        return create_driver(profile_dir, self.headless)
    
    def run_wallet(self, wallet: dict, action_count: int):
        wallet_id = wallet['id']
        address = wallet['address']
        self.logger.info(f'=== Wallet {wallet_id:02d} ({address[:8]}...) ===')
        
        driver = None
        try:
            driver = self.get_driver(wallet_id)
            
            # Claim faucets
            chains = ['sepolia', 'arbitrum_sepolia', 'optimism_sepolia', 'base_sepolia', 
                      'linea_sepolia', 'scroll_sepolia']
            results = claim_all_faucets(driver, address, chains)
            for chain, success in results.items():
                self.logger.info(f'  Faucet {chain}: {\"OK\" if success else \"FAIL\"}')
            
            # Run chain actions
            self.logger.info(f'  Running {action_count} chain actions...')
            for i in range(action_count):
                if not self.chain_farmers:
                    self.logger.warning('  No chain farmers initialized')
                    break
                chain_name = random.choice(list(self.chain_farmers.keys()))
                farmer = self.chain_farmers[chain_name]
                farmer.run_actions(1)
                time.sleep(random.uniform(
                    self.config['delays']['min_action_delay'],
                    self.config['delays']['max_action_delay']
                ))
            
            self.logger.info(f'  Wallet {wallet_id:02d} complete')
            
        except Exception as e:
            self.logger.error(f'  Wallet {wallet_id:02d} error: {e}')
            self.notifier.alert('ERROR', f'Wallet {wallet_id} failed', str(e))
        finally:
            if driver:
                driver.quit()
        
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
        
        # Send daily summary
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
    parser.add_argument('--headless', action='store_true', default=True)
    args = parser.parse_args()
    
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    
    password = os.environ.get('WALLET_PASSWORD')
    if not password:
        password = input('Wallet password: ')
    
    farmer = Farmer(config, password, headless=args.headless)
    
    if args.test_run:
        farmer.run(wallet_count=1)
    elif args.faucets_only:
        farmer.run(wallet_count=args.wallets, faucets_only=True)
    else:
        farmer.run(wallet_count=args.wallets)

if __name__ == '__main__':
    main()
