from __future__ import annotations
import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / '.data'
ARTIFACTS_DIR = DATA_DIR / 'artifacts'
DATA_DIR.mkdir(exist_ok=True)
ARTIFACTS_DIR.mkdir(exist_ok=True)
DATABASE_URL = os.getenv('DATABASE_URL', '')
SQLITE_PATH = str(DATA_DIR / 'bfsi.db')
REDIS_URL = os.getenv('REDIS_URL', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
LLM_MODEL = os.getenv('LLM_MODEL', 'claude-sonnet-5')
SEED_PARTIES = int(os.getenv('SEED_PARTIES', '8000'))
LATENCY_SLO_MS = float(os.getenv('LATENCY_SLO_MS', '98'))
DEV_PASSCODE = os.getenv('DEV_PASSCODE', 'Aryansh@Tredence')
DOMAINS = ['retail', 'corporate', 'wealth', 'asset_mgmt', 'payments', 'capital_markets', 'nbfc', 'personal_ins', 'general_ins', 'commercial_ins']
DOMAIN_LABELS = {'retail': 'Retail Banking', 'corporate': 'Corporate Banking', 'wealth': 'Wealth', 'asset_mgmt': 'Asset Management', 'payments': 'Payments', 'capital_markets': 'Capital Markets', 'nbfc': 'NBFC', 'personal_ins': 'Personal Insurance', 'general_ins': 'General Insurance', 'commercial_ins': 'Commercial Insurance'}
JOURNEY_STAGES = ['discover', 'originate', 'engage', 'cross_sell', 'service', 'retain']
CHANNELS = ['app', 'web', 'branch', 'call_center', 'sms', 'partner_api']
REGIONS = {'North America': 'USD', 'Europe': 'EUR', 'India': 'INR', 'APAC': 'SGD', 'LATAM': 'BRL', 'MEA': 'AED'}
CURRENCY_SYMBOL = {'USD': '$', 'EUR': '€', 'INR': '₹', 'SGD': 'S$', 'BRL': 'R$', 'AED': 'AED '}
FAIRNESS_GROUPS = ['group_a', 'group_b']
