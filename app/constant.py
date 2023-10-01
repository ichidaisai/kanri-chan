from dotenv import load_dotenv
from os import getenv

load_dotenv()


if (TOKEN := getenv("TOKEN")) is None:
    raise Exception("TOKEN is None")
if (SERVER_ID := getenv("SERVER_ID")) is None:
    raise Exception("SERVER_ID is None")
if (RELAYING_CATEGORY_ID := getenv("RELAYING_CATEGORY_ID")) is None:
    raise Exception("RELAYING_CATEGORY_ID is None")
if (NOTICE_CATEGORY_ID := getenv("NOTICE_CATEGORY_ID")) is None:
    raise Exception("NOTICE_CATEGORY_ID is None")
if (ALL_ANNOUNCE_CATEGORY_ID := getenv("ALL_ANNOUNCE_CATEGORY_ID")) is None:
    raise Exception("ALL_ANNOUNCE_CATEGORY_ID is None")
if (CAFE_ANNOUNCE_CATEGORY_ID := getenv("CAFE_ANNOUNCE_CATEGORY_ID")) is None:
    raise Exception("CAFE_ANNOUNCE_CATEGORY_ID is None")
if (MOGI_ANNOUNCE_CATEGORY_ID := getenv("MOGI_ANNOUNCE_CATEGORY_ID")) is None:
    raise Exception("MOGI_ANNOUNCE_CATEGORY_IDD is None")
if (CAFE_CONTACT_CATEGORY_ID := getenv("CAFE_CONTACT_CATEGORY_ID")) is None:
    raise Exception("CAFE_CONTACT_CATEGORY_ID is None")
if (MOGI_CONTACT_CATEGORY_ID := getenv("MOGI_CONTACT_CATEGORY_ID")) is None:
    raise Exception("MOGI_CONTACT_CATEGORY_ID is None")
if (ARCHIVE_CATEGORY_ID := getenv("ARCHIVE_CATEGORY_ID")) is None:
    raise Exception("ARCHIVE_CATEGORY_ID is None")
if (GOOGLE_DRIVE_FOLDER_ID := getenv("GOOGLE_DRIVE_FOLDER_ID")) is None:
    raise Exception("GOOGLE_DRIVE_FOLDER_ID is None")

try:
    SERVER_ID = int(SERVER_ID)
    RELAYING_CATEGORY_ID = int(RELAYING_CATEGORY_ID)
    NOTICE_CATEGORY_ID = int(NOTICE_CATEGORY_ID)
    ALL_ANNOUNCE_CATEGORY_ID = int(ALL_ANNOUNCE_CATEGORY_ID)
    CAFE_ANNOUNCE_CATEGORY_ID = int(CAFE_ANNOUNCE_CATEGORY_ID)
    MOGI_ANNOUNCE_CATEGORY_ID = int(MOGI_ANNOUNCE_CATEGORY_ID)
    CAFE_CONTACT_CATEGORY_ID = int(CAFE_CONTACT_CATEGORY_ID)
    MOGI_CONTACT_CATEGORY_ID = int(MOGI_CONTACT_CATEGORY_ID)
    ARCHIVE_CATEGORY_ID = int(ARCHIVE_CATEGORY_ID)
except ValueError:
    raise ValueError("正しく環境変数を指定してください。")
