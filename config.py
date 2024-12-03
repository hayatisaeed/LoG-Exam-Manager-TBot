import os

# config.py
BOT_TOKEN = "8042887753:AAFF9FBEuEgcyeqVnsPC06_KMw2gAsF7Q64"

# SQLite database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db/exam_manager.db")

# Flask secret key for sessions
SECRET_KEY = os.getenv("SECRET_KEY", "secret_key")

