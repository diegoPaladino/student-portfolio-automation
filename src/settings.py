from pathlib import Path
import os
ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get('PORTFOLIO_DATA_DIR', ROOT / 'data')).resolve()
IMAGES = DATA / 'images'
DB = DATA / 'portfolio.sqlite3'
MAX_BYTES = 30 * 1024 * 1024
