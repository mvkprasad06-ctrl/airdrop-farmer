import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def create_driver(profile_dir: str, headless: bool = True) -> webdriver.Chrome:
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
    opts.add_argument('--disable-extensions')
    opts.add_argument('--disable-plugins')
    opts.add_argument('--disable-background-timer-throttling')
    opts.add_argument('--disable-backgrounding-occluded-windows')
    opts.add_argument('--disable-renderer-backgrounding')
    opts.add_argument('--disable-features=TranslateUI,BlinkGenPropertyTrees')
    opts.add_argument('--no-zygote')
    opts.add_argument('--single-process')
    import random
    w = 1280 + random.randint(-50, 50)
    h = 720 + random.randint(-50, 50)
    opts.add_argument(f'--window-size={w},{h}')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_page_load_timeout(60)
    return driver

def get_profile_dir(base: str, wallet_id: int) -> str:
    path = os.path.join(base, f'wallet_{wallet_id:03d}')
    os.makedirs(path, exist_ok=True)
    return path