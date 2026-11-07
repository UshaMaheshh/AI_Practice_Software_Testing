import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

BASE_URL = os.getenv(
    "TARGET_URL",
    "https://practicesoftwaretesting.com/"
)

HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

SCREENSHOT_DIR = BASE_DIR / "screenshots"
LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"

for folder in [SCREENSHOT_DIR, LOG_DIR, REPORT_DIR]:
    folder.mkdir(parents=True, exist_ok=True)
BROWSER_PAUSE_SECONDS = 10