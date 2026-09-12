import psutil
import json
from pathlib import Path
from datetime import datetime, timedelta

def collect_stats(logs_dir: str = 'logs', state_file: str = 'state/state.json') -> dict:
    stats = {
        'wallets': 0,
        'chains': 5,
        'txns': 0,
        'faucet_rate': 0.0,
        'errors': 0,
        'cpu_avg': psutil.cpu_percent(interval=1),
        'ram_avg': psutil.virtual_memory().percent,
    }
    # Parse recent logs for txns/errors
    log_files = list(Path(logs_dir).glob('farmer_*.log'))
    if log_files:
        latest = max(log_files, key=lambda f: f.stat().st_mtime)
        try:
            lines = latest.read_text(encoding='utf-8', errors='ignore').splitlines()
            recent = lines[-200:]  # Last 200 lines
            stats['txns'] = sum(1 for l in recent if 'txn' in l.lower() or 'bridge' in l.lower() or 'swap' in l.lower())
            stats['errors'] = sum(1 for l in recent if 'error' in l.lower() or 'exception' in l.lower())
            faucet_ok = sum(1 for l in recent if 'faucet' in l.lower() and 'ok' in l.lower())
            faucet_total = sum(1 for l in recent if 'faucet' in l.lower())
            stats['faucet_rate'] = faucet_ok / faucet_total if faucet_total else 0.0
        except Exception:
            pass
    # Load wallet count
    if Path(state_file).exists():
        try:
            stats['wallets'] = len(json.loads(Path(state_file).read_text()).get('nonces', {}))
        except Exception:
            pass
    return stats

if __name__ == '__main__':
    print(json.dumps(collect_stats(), indent=2))
