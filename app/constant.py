from dotenv import load_dotenv
from os import getenv

load_dotenv()

try:
    TOKEN = getenv("TOKEN")
    SERVER_ID = int(getenv("SERVER_ID"))
    RELAYING_CATEGORY_ID = int(getenv("RELAYING_CATEGORY_ID"))
    NOTICE_CATEGORY_ID = int(getenv("NOTICE_CATEGORY_ID"))
    GOOGLE_DRIVE_FOLDER_ID = getenv("GOOGLE_DRIVE_FOLDER_ID")
except Exception:
    raise Exception("必要な環境変数が正しく指定されていません。")
