import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

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
    opts.add_argument('--disable-setuid-sandbox')
    opts.add_argument('--disable-infobars')
    opts.add_argument('--disable-breakpad')
    opts.add_argument('--disable-crash-reporter')
    opts.add_argument('--disable-dev-tools')
    opts.add_argument('--disable-extensions-http-throttling')
    opts.add_argument('--disable-ipc-flooding-protection')
    opts.add_argument('--password-store=basic')
    opts.add_argument('--use-mock-keychain')
    opts.add_argument('--enable-unsafe-swiftshader')
    opts.add_argument('--use-gl=swiftshader')
    opts.add_argument('--disable-gpu-sandbox')
    opts.add_argument('--disable-accelerated-2d-canvas')
    opts.add_argument('--disable-accelerated-video-decode')
    import random
    w = 1280 + random.randint(-50, 50)
    h = 720 + random.randint(-50, 50)
    opts.add_argument(f'--window-size={w},{h}')
    
    # Use chromedriver from selenium/standalone-chrome image
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_page_load_timeout(60)
    return driver

def get_profile_dir(base: str, wallet_id: int) -> str:
    path = os.path.join(base, f'wallet_{wallet_id:03d}')
    os.makedirs(path, exist_ok=True)
    return path