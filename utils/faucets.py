import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FAUCETS = {
    'sepolia': [
        {'url': 'https://faucet.quicknode.com/ethereum/sepolia', 'selector': "input[name='address']", 'btn': "button[type='submit']"},
        {'url': 'https://www.alchemy.com/faucets/ethereum-sepolia', 'selector': 'input#address', 'btn': "button[type='submit']"},
        {'url': 'https://sepoliafaucet.com/', 'selector': "input[name='address']", 'btn': "button[type='submit']"},
    ],
    'arbitrum_sepolia': [
        {'url': 'https://faucet.quicknode.com/arbitrum/sepolia', 'selector': "input[name='address']", 'btn': "button[type='submit']"},
    ],
    'optimism_sepolia': [
        {'url': 'https://faucet.quicknode.com/optimism/sepolia', 'selector': "input[name='address']", 'btn': "button[type='submit']"},
    ],
    'base_sepolia': [
        {'url': 'https://faucet.quicknode.com/base/sepolia', 'selector': "input[name='address']", 'btn': "button[type='submit']"},
    ],
    'linea_sepolia': [
        {'url': 'https://faucet.linea.build', 'selector': "input[placeholder*='address']", 'btn': "button[type='submit']"},
    ],
    'scroll_sepolia': [
        {'url': 'https://faucet.scroll.io', 'selector': "input[name='address']", 'btn': "button[type='submit']"},
    ],
}

def claim_faucet(driver, chain: str, address: str) -> bool:
    for faucet in FAUCETS.get(chain, []):
        try:
            driver.get(faucet['url'])
            time.sleep(random.uniform(2, 5))
            inp = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, faucet['selector'])))
            inp.clear()
            inp.send_keys(address)
            time.sleep(random.uniform(0.5, 1.5))
            btn = driver.find_element(By.CSS_SELECTOR, faucet['btn'])
            btn.click()
            time.sleep(random.uniform(3, 8))
            page = driver.page_source.lower()
            if any(kw in page for kw in ['success', 'sent', 'claimed', 'txid', 'transaction']):
                return True
        except Exception:
            continue
    return False

def claim_all_faucets(driver, address: str, chains: list[str]) -> dict:
    results = {}
    for chain in chains:
        results[chain] = claim_faucet(driver, chain, address)
        time.sleep(random.uniform(5, 15))
    return results