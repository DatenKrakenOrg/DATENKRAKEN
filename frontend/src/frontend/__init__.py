import os

if os.getenv("ENVIRONMENT") != "PROD":
    from dotenv import load_dotenv
    load_dotenv()

from utility.datafetcher import DataFetcher
from frontend.functions import  load_config

# Constants
FETCHER = DataFetcher()
STATUS_COLORS = {"optimal": "green", "warning": "yellow", "critical": "red"}
CONFIG = load_config()
ROOMS = FETCHER.get_unique_arduino_ids()