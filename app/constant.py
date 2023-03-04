from dotenv import load_dotenv
from os import getenv

load_dotenv()

try:
    TOKEN = getenv("TOKEN")
    SERVER_ID = int(getenv("SERVER_ID"))
    RELAYING_CATEGORY_ID = int(getenv("RELAYING_CATEGORY_ID"))
except Exception:
    raise Exception("必要な環境変数が正しく指定されていません。")

if not isinstance(TOKEN, str):
    raise Exception("TOKEN が正しく指定されていません。")
if not isinstance(SERVER_ID, int):
    raise Exception("SERVER_ID が正しく指定されていません。")
if not isinstance(RELAYING_CATEGORY_ID, int):
    raise Exception("RELAYING_CATEGORY_ID が正しく指定されていません。")
