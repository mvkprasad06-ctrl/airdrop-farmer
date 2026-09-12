import os
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

def create_driver(profile_dir: str, headless: bool = True) -> uc.Chrome:
    opts = Options()
    opts.add_argument(f'--user-data-dir={profile_dir}')
    opts.add_argument('--no-first-run')
    opts.add_argument('--no-default-browser-check')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--no-sandbox')
    if headless:
        opts.add_argument('--headless=new')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--disable-software-rasterizer')
    opts.add_argument('--memory-pressure-off')
    opts.add_argument('--max_old_space_size=512')
    import random
    w = 1280 + random.randint(-50, 50)
    h = 720 + random.randint(-50, 50)
    opts.add_argument(f'--window-size={w},{h}')
    driver = uc.Chrome(options=opts, version_main=None)
    driver.set_page_load_timeout(60)
    return driver

def get_profile_dir(base: str, wallet_id: int) -> str:
    path = os.path.join(base, f'wallet_{wallet_id:03d}')
    os.makedirs(path, exist_ok=True)
    return path
