import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "-1001894076476")
CHANNELS = [
    "UCM7-8EfoIv0T9cCI4FhHbKQ",
    "UC6bTF68IAV1okfRfwXIP1Cg"
]
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", 120))