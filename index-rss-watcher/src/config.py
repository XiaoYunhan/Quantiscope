from dotenv import load_dotenv
from pathlib import Path
import os
import warnings

# Suppress SSL/urllib3 warnings
warnings.filterwarnings("ignore", message="urllib3.*")
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=False)

FEED_URL          = os.getenv("FEED_URL", "https://www.spglobal.com/spdji/en/rss/rss-details/?rssFeedName=index-news-announcements")
POLL_INTERVAL_SEC = int(os.getenv("POLL_INTERVAL_SEC", 30))      # 轮询间隔
DB_PATH           = os.getenv("DB_PATH",   "./rss_state.db")

# Twilio
TWILIO_SID        = os.getenv("TWILIO_SID")
TWILIO_TOKEN      = os.getenv("TWILIO_TOKEN")
TWILIO_FROM       = os.getenv("TWILIO_FROM")      # 购买的号码
TWILIO_TO         = os.getenv("TWILIO_TO")        # 目标手机号
USE_VOICE         = bool(int(os.getenv("USE_VOICE", 0)))         # 0=短信；1=语音
