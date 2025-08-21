import os

if os.getenv("ENVIRONMENT") != "PROD":
    from dotenv import load_dotenv
    load_dotenv()

