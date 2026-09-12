"""Web3.py-based chain actions - no browser needed"""
import random
import time
from typing import Dict, Optional
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.signers.local import LocalAccount

ERC20_ABI = '''[
    {"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},
    {"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"type":"function"},
    {"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"type":"function"},
    {"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"type":"function"}
]'''

# Known testnet contract addresses
CONTRACTS = {
    'arbitrum_sepolia': {
        'usdc': '0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d',
        'stargate_router': '0xB0D502E93887fE1aA4E8b3A4C8C8C8C8C8C8C8C8C',
    },
    'optimism_sepolia': {
        'usdc': '0x5fd84259d66Cd46123540766Be93DFE6D43130D7',
        'stargate_router': '0xB0D502E93887fE1aA4E8b3A4C8C8C8C8C8C8C8C8C',
    },
    'base_sepolia': {
        'usdc': '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
    },
    'linea_sepolia': {
        'syncswap_router': '0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295',
    },
    'scroll_sepolia': {
        'skydrome_router': '0x4a6F721183D8b750e1AEa49C5be5318A7214F3e3',
    },
}

class Web3Actions:
    def __init__(self, w3_dict: Dict[str, Web3], config: dict, logger):
        self.w3 = w3_dict
        self.config = config
        self.logger = logger
        
        # Add POA middleware for chains that need it
        for name, w3 in w3_dict.items():
            if name in ['arbitrum_sepolia', 'optimism_sepolia', 'base_sepolia', 'linea_sepolia', 'scroll_sepolia']:
                w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    def get_account(self, private_key: str) -> LocalAccount:
        return Account.from_key(private_key)
    
    def get_balance(self, chain: str, address: str, token_address: Optional[str] = None) -> int:
        w3 = self.w3.get(chain)
        if not w3:
            return 0
        if token_address:
            contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
            return contract.functions.balanceOf(Web3.to_checksum_address(address)).call()
        return w3.eth.get_balance(Web3.to_checksum_address(address))
    
    def send_native_transfer(self, chain: str, account: LocalAccount, to: str, amount_wei: int) -> str:
        w3 = self.w3[chain]
        nonce = w3.eth.get_transaction_count(account.address)
        tx = {
            'nonce': nonce,
            'to': Web3.to_checksum_address(to),
            'value': amount_wei,
            'gas': 21000,
            'gasPrice': w3.eth.gas_price,
            'chainId': w3.eth.chain_id,
        }
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        return w3.to_hex(tx_hash)
    
    def send_erc20_transfer(self, chain: str, account: LocalAccount, token: str, to: str, amount: int) -> str:
        w3 = self.w3[chain]
        contract = w3.eth.contract(address=Web3.to_checksum_address(token), abi=ERC20_ABI)
        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.transfer(Web3.to_checksum_address(to), amount).build_transaction({
            'nonce': nonce,
            'gas': 100000,
            'gasPrice': w3.eth.gas_price,
            'chainId': w3.eth.chain_id,
        })
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        return w3.to_hex(tx_hash)
    
    def approve_token(self, chain: str, account: LocalAccount, token: str, spender: str, amount: int) -> str:
        w3 = self.w3[chain]
        contract = w3.eth.contract(address=Web3.to_checksum_address(token), abi=ERC20_ABI)
        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.approve(Web3.to_checksum_address(spender), amount).build_transaction({
            'nonce': nonce,
            'gas': 100000,
            'gasPrice': w3.eth.gas_price,
            'chainId': w3.eth.chain_id,
        })
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        return w3.to_hex(tx_hash)
    
    def execute_random_action(self, chain: str, address: str, private_key: str):
        """Execute a random action on the given chain."""
        account = self.get_account(private_key)
        w3 = self.w3.get(chain)
        if not w3:
            raise ValueError(f'No RPC for chain {chain}')
        
        actions = []
        
        # Native transfer (small amount)
        if w3.eth.get_balance(account.address) > w3.to_wei(0.001, 'ether'):
            actions.append(('native_transfer', lambda: self.send_native_transfer(
                chain, account, '0x0000000000000000000000000000000000000000', 
                random.randint(100000000000000, 500000000000000)  # 0.0001-0.0005 ETH
            )))
        
        # ERC20 transfers if tokens available
        contracts = CONTRACTS.get(chain, {})
        for token_name, token_addr in contracts.items():
            if token_name in ['usdc', 'weth']:
                balance = self.get_balance(chain, address, token_addr)
                if balance > 1000000:  # > 1 USDC
                    actions.append((f'{token_name}_transfer', lambda t=token_addr: self.send_erc20_transfer(
                        chain, account, t, '0x0000000000000000000000000000000000000000',
                        random.randint(1000000, 5000000)
                    )))
        
        if actions:
            action_name, action_fn = random.choice(actions)
            try:
                tx_hash = action_fn()
                self.logger.info(f'  [{chain}] {action_name}: {tx_hash}')
                return tx_hash
            except Exception as e:
                self.logger.error(f'  [{chain}] {action_name} failed: {e}')
                raise
        else:
            self.logger.info(f'  [{chain}] No actions available (insufficient balance)')
    
    def run_layerzero_bridge(self, account: LocalAccount, from_chain: str, to_chain: str, amount_wei: int) -> str:
        """Bridge via Stargate (simplified - just native transfer for demo)."""
        # Real implementation would use Stargate contracts
        return self.send_native_transfer(from_chain, account, '0x0000000000000000000000000000000000000000', amount_wei)