import os
import io
import logging
import random
import datetime
import sqlite3
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo, InputMediaPhoto
import qrcode

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_RAW = os.getenv("ADMIN_ID", "").strip()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing")

if not ADMIN_RAW.isdigit():
    raise RuntimeError("ADMIN_ID missing or invalid")

ADMIN_ID = int(ADMIN_RAW)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# =========================================================
# LOGGING & DATABASE SETUP
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)

DB_PATH = "/app/data/bot_database.db" if os.path.exists("/app/data") else "bot_database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS demos (id INTEGER PRIMARY KEY AUTOINCREMENT, plan_id INTEGER, media_type TEXT, file_id TEXT)")
    conn.commit()
    
    cursor.execute("SELECT value FROM settings WHERE key='current_upi'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO settings (key, value) VALUES ('current_upi', 'haaland78@ybl')")
        conn.commit()
    conn.close()

init_db()

def get_current_upi():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key='current_upi'")
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else "haaland78@ybl"

def set_current_upi(new_upi):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE settings SET value=? WHERE key='current_upi'", (new_upi,))
    conn.commit()
    conn.close()

def add_user_db(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

SUPPORT_LINK = "https://t.me/xylerigcc"
WELCOME_IMAGE = "https://ibb.co/RGL77cpn"
START_IMAGE = ""

# =========================================================
# 10 PLANS WITH HOSTED DEMO URLS
# =========================================================

PLANS = [
    {
        "id": 1,
        "name": "🔥 Plan 1",
        "price": "49",
        "validity": "180 days",
        "videos": "45000+",
        "demos": [
            {"type": "video", "id": "https://videotourl.com/videos/1791609530271-d1845e11-78bd-4465-a0e3-3e0dd57fb424.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791610410648-c50ab2d2-b1b2-4998-8f5f-43a5f719b603.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791609652325-1646ca32-e73f-4a5a-9874-a0f4e401c6bb.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791609624603-358124e2-dbc4-43b2-9772-e18c1df57397.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791609569957-a7ce2e8a-e185-4dc6-893c-298a2d9c1b4c.mp4"}
        ],
        "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "active": True
    },
    {
        "id": 2,
        "name": "🔥 Plan 2",
        "price": "69",
        "validity": "180 days",
        "videos": "40000+",
        "demos": [
            {"type": "video", "id": "https://videotourl.com/videos/1791598317965-12b2368c-6035-4e43-b708-df28bcd246b6.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791609986226-0b727823-bf05-42b7-80e8-c949f04b95ab.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598333066-6d6fc74f-945c-4641-99d1-d862e59790d4.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598348006-882fbe39-db59-4bb7-8636-1c2645fb93c0.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791611260635-789f7a13-25cd-4204-8ffc-455168319040.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598360862-d0ddd962-c4e7-4c98-a860-d360bf6779f8.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791601968259-cb7b49a5-a8c5-45f9-9156-e08f71b052d0.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598382840-4245fa8e-38f8-4737-8bb9-a2b8641a3d0f.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598397313-ff9dd5ef-d489-4715-a2ca-a71c8923f162.mp4"}
        ],
        "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "active": True
    },
    {
        "id": 3,
        "name": "🔥 Plan 3",
        "price": "49",
        "validity": "180 days",
        "videos": "70000+",
        "demos": [
            {"type": "video", "id": "https://videotourl.com/videos/1791598226633-9d219b40-bf0b-4774-b493-6449c47d5ef1.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598035486-79178a34-a631-49d2-870e-ff3425f1c058.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791611314862-1e0e5b81-0a04-436a-9749-4f5e9115404f.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598059935-f6722923-e315-4b97-aaeb-e7b0af379f2b.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598126801-a117ace0-e399-46e6-b697-0d3da6efeedd.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598104865-7bca6c3f-db24-465d-9688-d153131af1e5.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598207010-15f8101c-d87e-4e83-bd6a-43a333204662.mp4"}
        ],
        "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "active": True
    },
    {
        "id": 4,
        "name": "🔥 Plan 4",
        "price": "39",
        "validity": "180 days",
        "videos": "56000+",
        "demos": [
            {"type": "video", "id": "https://videotourl.com/videos/1791611037316-4db456f2-f82c-4468-9f48-381341ed6e55.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791611085614-c863517b-d989-4d6f-b6ef-d23db0b73f5a.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791611220352-ba6538bc-4db1-401e-81f7-88c53824e27f.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791609479203-02acf86c-6132-4bc2-8041-9f43ab529748.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791611168222-86d679dd-8a24-46fb-8b06-d59cc97e84c2.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791611005214-c25159ac-d514-4eff-8061-a25465ff6eba.mp4"}
        ],
        "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "active": True
    },
    {
        "id": 5,
        "name": "🔥 Plan 5",
        "price": "49",
        "validity": "180 days",
        "videos": "67000+",
        "demos": [
            {"type": "video", "id": "https://videotourl.com/videos/1791611423923-36dbbbf3-84c1-4754-a7e4-dc05798eaa03.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791611350514-052fe889-5ac7-4446-91ef-2f928070e131.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791609591492-b5b0f616-27c5-436f-9aa9-e70720337677.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791609952353-7ee9382f-6db6-4c43-86ed-c8f418a3282c.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791609450717-98fd3d4d-533c-46fc-a290-9f9f937b6721.mp4"}
        ],
        "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "active": True
    },
    {
        "id": 6,
        "name": "🔥 Plan 6",
        "price": "49",
        "validity": "180 days",
        "videos": "50000+",
        "demos": [
            {"type": "video", "id": "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791607674607-203922d8-e261-4085-90fc-4be2fd62a6fb.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791607662133-116f8c11-861a-4d4c-94a4-411fbd79a4f4.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791607553470-a87b7709-29e5-449b-89d2-49ce97c8e367.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791607607288-b1cc3341-7d49-473e-8544-840992806dab.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791607585444-8a7d8e39-2917-4d23-949e-c048fcbacb2f.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791607617748-9c8da0dd-313e-4a4d-862b-7ccf034383b7.mp4"}
        ],
        "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "active": True
    },
    {
        "id": 7,
        "name": "🔥 Plan 7",
        "price": "58",
        "validity": "180 days",
        "videos": "30000+",
        "demos": [
            {"type": "video", "id": "https://videotourl.com/videos/1791609855846-9b6bac98-1fcf-4d60-b612-3e5abaf6be7e.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791614058029-1220e2df-44c4-467d-bbd7-755af32ada0c.mp4"}
        ],
        "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "active": True
    },
    {
        "id": 8,
        "name": "🔥 Plan 8",
        "price": "63",
        "validity": "180 days",
        "videos": "70000+",
        "demos": [
            {"type": "video", "id": "https://videotourl.com/videos/1791611593469-187437c5-8f84-41c6-afa1-3d61feb9ff72.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791611552865-c2cf6f7d-1544-4c34-9bdb-5e5fb2092584.mp4"}
        ],
        "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙁𝙍𝙄𝘿𝘼𝙔 ✅.",
        "active": True
    },
    {
        "id": 9,
        "name": "🔥 Plan 9",
        "price": "49",
        "validity": "180 days",
        "videos": "18000+",
        "demos": [
            {"type": "video", "id": "https://videotourl.com/videos/1791611713436-2f106a4b-9ee1-4d9b-8e06-c30a0fe309e7.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791611779829-f05b75a9-65c7-441d-ad89-5d5f15301b01.mp4"}
        ],
        "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "active": True
    },
    {
        "id": 10,
        "name": "𝗔𝗟𝗟 𝗩𝗜𝗣 𝗠𝗘𝗚𝗔 𝗣𝗔𝗖𝗞 🔥",
        "price": "169",
        "validity": "180 days",
        "videos": "100000+",
        "demos": [],
        "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅",
        "active": True
    }
]

STYLE_SERIES = ["danger", "success", "primary", "danger", "success", "primary"]

def button(text, data=None, url=None, style=None):
    kwargs = {"text": text}
    if data is not None: kwargs["callback_data"] = data
    if url is not None: kwargs["url"] = url
    if style is not None: kwargs["style"] = style
    return InlineKeyboardButton(**kwargs)

def add_styled(kb, text, data=None, url=None, index=0):
    style = STYLE_SERIES[index % len(STYLE_SERIES)]
    kb.add(button(text, data=data, url=url, style=style))

def get_plan(pid):
    for plan in PLANS:
        if plan["id"] == pid and plan.get("active"):
            return plan
    return None

def generate_upi_qr(upi_id: str, amount: float, payee_name: str = "VIP Access") -> io.BytesIO:
    upi_url = f"upi://pay?pa={upi_id}&pn={payee_name}&am={amount:.2f}&cu=INR"
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(upi_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def generate_txn_id(plan_id: int) -> str:
    date_str = datetime.datetime.now().strftime("%y%m%d")
    rand_str = f"{random.randint(1000, 9999)}"
    return f"TXN-{date_str}-{plan_id}-{rand_str}"

def send_photo_or_text(chat_id, image, caption, reply_markup=None):
    if not image:
        bot.send_message(chat_id, caption, reply_markup=reply_markup)
        return
    try:
        bot.send_photo(chat_id, image, caption=caption, reply_markup=reply_markup)
    except Exception:
        log.exception("Could not send configured image")
        bot.send_message(chat_id, caption, reply_markup=reply_markup)

# =========================================================
# START & HOME SCREENS
# =========================================================

START_CAPTION = " 𝘽𝙚𝙛𝙤𝙧𝙚 𝙘𝙤𝙣𝙩𝙞𝙣𝙪𝙞𝙣𝙜, 𝙥𝙡𝙚𝙖𝙨𝙚 𝙘𝙤𝙣𝙛𝙞𝙧𝙢 𝙮𝙤𝙪 𝙖𝙧𝙚 18 𝙤𝙧 𝙤𝙡𝙙𝙚𝙧."

def send_start_screen(chat_id):
    kb = InlineKeyboardMarkup()
    kb.row(
        button(" 𝙔𝙀𝙎 𝙄 𝘼𝙈 18+ ✅", data="free", style="success"),
        button("𝙄 𝘼𝙈 𝙉𝙊𝙏 18+ ❌", data="paid_warning", style="danger")
    )
    send_photo_or_text(chat_id, START_IMAGE, START_CAPTION, kb)

def send_paid_screen(chat_id):
    kb = InlineKeyboardMarkup()
    add_styled(kb, "🔙 𝘽𝘼𝘾𝙆", data="start", index=2)
    bot.send_message(chat_id, " <b>𝙏𝙃𝙄𝙎 𝘽𝙊𝙏 𝙄𝙎 𝙊𝙉𝙇𝙔 𝙁𝙊𝙍 18+ 𝙐𝙎𝙀𝙍𝙎‼️</b>\n\n", reply_markup=kb)

WELCOME_CAPTION = (
    "<b> 𝙃𝙀𝙔 👋🏻, 𝙒𝙚𝙡𝙘𝙤𝙢ε 𝙩𝙤 𝙤𝙪𝙧 𝙫𝙞𝙥 𝙗𝙤𝙩  😍</b> \n\n"
    "𝙏𝙃𝙄𝙎 𝘽𝙊𝙏 𝘾𝙊𝙉𝘼𝙏𝘼𝙄𝙉 𝙁𝙊𝙇𝙇𝙊𝙒𝙄𝙉𝙂 𝙋𝙇𝘼𝙉𝙎 ✅\n"
    "𝙎𝙏𝘼𝙍𝙏𝙄𝙉𝙂 𝙋𝙍𝙄𝘾𝙀 𝙄𝙎 𝙅𝙐𝙎𝙏 ₹39 ‼️\n\n"
    "𝘽𝙀𝙉𝙄𝙁𝙄𝙏𝙎 𝙊𝙐𝙍 𝘽𝙊𝙏 ✅ \n"
    "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙑𝙄𝘿𝙀𝙊𝙎 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅ \n"
    "2. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝘿𝙊𝙒𝙉𝙇𝙊𝘼𝘿 𝙁𝙍𝙀𝙀 ✅ \n"
    "3. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ✅ \n"
    "4. 𝘿𝙄𝙍𝙀𝘾𝙏 𝙒𝘼𝙏𝘾𝙃 𝙑𝙄𝘿𝙀𝙊𝙎 ✅ \n"
    "<b>𝙏𝙊 𝘽𝙐𝙔 𝙋𝙇𝘼𝙉𝙎 𝘾𝙃𝙀𝘾𝙆 𝘽𝙐𝙏𝙏𝙊𝙉𝙎 𝘽𝙀𝙇𝙊𝙒 𝘼𝙉𝘿 𝘾𝙃𝙀𝘾𝙆 𝘿𝙀𝙈𝙊 𝘼𝙇𝙎𝙊</b> 😍🔥"
)

def send_home(chat_id):
    kb = InlineKeyboardMarkup()
    active_plans = [p for p in PLANS if p.get("active")]
    for i, p in enumerate(active_plans):
        add_styled(kb, f" {p['name']} · ₹{p['price']}", data=f"plan:{p['id']}", index=i)

    add_styled(kb, "🎬 𝘿𝙀𝙈𝙊", data="demo_menu", index=0)
    add_styled(kb, " 𝙎𝙐𝙋𝙋𝙊𝙍𝙏📞", url=SUPPORT_LINK, index=1)
    send_photo_or_text(chat_id, WELCOME_IMAGE, WELCOME_CAPTION, kb)

def send_demo_menu(chat_id):
    kb = InlineKeyboardMarkup()
    active_plans = [p for p in PLANS if p.get("active")]
    for i, p in enumerate(active_plans):
        add_styled(kb, f"🎬 {p['name']}", data=f"demo_plan:{p['id']}", index=i)
    add_styled(kb, "🔙 𝘽𝘼𝘾𝙆", data="home", index=2)
    bot.send_message(chat_id, "🎬 <b>𝘿𝙀𝙈𝙊</b>\n\n𝘿𝙚𝙢𝙤 𝙙𝙚𝙠𝙝𝙣𝙚 𝙠𝙚 𝙡𝙞𝙮𝙚 𝙠𝙤𝙞 𝙥𝙡𝙖𝙣 𝙨𝙚𝙡𝙚𝙘𝙩 𝙠𝙖𝙧𝙤.\n\n👇 <b>𝙎𝙚𝙡𝙚𝙘𝙩 𝙖 𝙥𝙡𝙖𝙣:</b>", reply_markup=kb)

# =========================================================
# PLAN DETAILS & MEDIA GROUP DEMOS
# =========================================================

def send_plan(chat_id, plan):
    # Plan 10 Direct Payment QR
    if plan["id"] == 10:
        send_payment(chat_id, chat_id, plan)
        return

    demos = plan.get("demos", [])
    if demos:
        media_group = []
        for media in demos:
            if media["type"] == "photo":
                media_group.append(InputMediaPhoto(media["id"], has_spoiler=True))
            elif media["type"] == "video":
                media_group.append(InputMediaVideo(media["id"], has_spoiler=True))
        
        try:
            bot.send_media_group(chat_id, media_group)
        except Exception as e:
            log.exception(f"Error sending media group: {e}")

    caption = (
        f"📦 <b>{plan['name']}</b>\n\n"
        f"💰 <b>𝙋𝙧𝙞𝙘𝙚:</b> ₹{plan['price']}\n"
        f"⏳ <b>𝙑𝙖𝙡𝙞𝙙𝙞𝙩𝙮:</b> {plan['validity']}\n"
        f"🎬 <b>𝙑𝙞𝙙𝙚𝙊𝙎:</b> {plan['videos']}\n\n"
        f"{plan['caption']}"
    )
    kb = InlineKeyboardMarkup()
    kb.row(button("🟢 𝘽𝙐𝙔 𝙉𝙊𝙒 💳", data=f"buy:{plan['id']}", style="success"))
    kb.row(button("🔵 𝘽𝘼𝘾𝙆 𝙏𝙊 𝙋𝙇𝘼𝙉𝙎", data="home", style="primary"))
    
    bot.send_message(chat_id, caption, parse_mode="HTML", reply_markup=kb)

def send_payment(chat_id, user_id, plan):
    current_upi = get_current_upi()
    txn_id = generate_txn_id(plan["id"])
    
    try:
        qr_buffer = generate_upi_qr(current_upi, float(plan["price"]))
        qr_buffer.seek(0)
    except Exception as e:
        log.exception(f"QR Error: {e}")
        bot.send_message(chat_id, "❌ QR code generation error.")
        return

    kb = InlineKeyboardMarkup()
    kb.row(button("🟢 𝙄 𝙋𝘼𝙄𝘿 ✅", data=f"paid:{plan['id']}:{txn_id}", style="success"))
    kb.row(button("🔵 𝘽𝘼𝘾𝙆 ⬅️", data="home", style="primary"))

    caption = (
        f"💳 <b>𝙋𝘼𝙔𝙈𝙀𝙉𝙏 𝙋𝘼𝙂𝙀</b>\n\n"
        f"📦 <b>Plan:</b> {plan['name']}\n"
        f"💰 <b>Amount:</b> ₹{plan['price']}\n"
        f"🆔 <b>TXN:</b> <code>{txn_id}</code>\n"
        f"💎 <b>UPI:</b> <code>{current_upi}</code> (tap to copy)\n\n"
        "1️⃣ Scan QR or copy UPI ID.\n"
        "2️⃣ Pay exact amount.\n"
        "3️⃣ Click <b>𝙄 𝙋𝘼𝙄𝘿 ✅</b> & send screenshot."
    )

    bot.send_photo(chat_id, photo=qr_buffer, caption=caption, parse_mode="HTML", reply_markup=kb)
    waiting_screenshot.add(user_id)
    pending_orders[user_id] = {"plan_id": plan["id"], "txn_id": txn_id}

waiting_screenshot = set()
pending_orders = {}

# =========================================================
# HANDLERS
# =========================================================

@bot.message_handler(commands=["start"])
def start(message):
    add_user_db(message.from_user.id)
    send_start_screen(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "free")
def free_button(call):
    bot.answer_callback_query(call.id)
    send_home(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "paid_warning")
def paid_warning_button(call):
    bot.answer_callback_query(call.id)
    send_paid_screen(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "start")
def start_back(call):
    bot.answer_callback_query(call.id)
    send_start_screen(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "home")
def home_button(call):
    bot.answer_callback_query(call.id)
    send_home(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "demo_menu")
def demo_button(call):
    bot.answer_callback_query(call.id)
    send_demo_menu(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("plan:"))
def plan_button(call):
    bot.answer_callback_query(call.id)
    try:
        plan_id = int(call.data.split(":")[1])
    except Exception:
        return
    plan = get_plan(plan_id)
    if plan:
        send_plan(call.message.chat.id, plan)

@bot.callback_query_handler(func=lambda call: call.data.startswith("demo_plan:"))
def demo_plan_button(call):
    bot.answer_callback_query(call.id)
    try:
        plan_id = int(call.data.split(":")[1])
    except Exception:
        return
    plan = get_plan(plan_id)
    if plan:
        send_plan(call.message.chat.id, plan)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy:"))
def buy_button(call):
    bot.answer_callback_query(call.id)
    try:
        plan_id = int(call.data.split(":")[1])
    except Exception:
        return
    plan = get_plan(plan_id)
    if plan:
        send_payment(call.message.chat.id, call.from_user.id, plan)

@bot.callback_query_handler(func=lambda call: call.data.startswith("paid:"))
def paid_confirm(call):
    bot.answer_callback_query(call.id)
    try:
        parts = call.data.split(":")
        plan_id = int(parts[1])
    except Exception:
        return
    plan = get_plan(plan_id)
    if not plan:
        return
    uid = call.from_user.id
    waiting_screenshot.add(uid)
    bot.send_message(call.message.chat.id, "📸 <b>𝙎𝙚𝙣𝙙 𝙮𝙤𝙪𝙧 𝙥𝙖𝙮𝙢𝙚𝙣𝙩 𝙨𝙘𝙧𝙚𝙚𝙣𝙨𝙝𝙤𝙩 𝙖𝙨 𝙖 𝙥𝙝𝙤𝙩𝙤.</b>", parse_mode="HTML")

@bot.message_handler(content_types=["photo"])
def screenshot_handler(message):
    uid = message.from_user.id
    if uid not in waiting_screenshot:
        return
    
    order = pending_orders.get(uid, {})
    plan_id = order.get("plan_id", 1)
    txn_id = order.get("txn_id", "N/A")
    plan = get_plan(plan_id)
    plan_name = plan["name"] if plan else "VIP Plan"

    waiting_screenshot.discard(uid)
    pending_orders.pop(uid, None)

    screenshot_id = message.photo[-1].file_id

    admin_kb = InlineKeyboardMarkup()
    admin_kb.row(
        button("🟢 APPROVE", callback_data=f"admin_approve:{uid}:{plan_id}:{txn_id}", style="success"),
        button("🔴 REJECT", callback_data=f"admin_reject:{uid}", style="danger")
    )

    bot.send_photo(
        ADMIN_ID,
        screenshot_id,
        caption=(
            f"📥 <b>NEW PAYMENT PROOF</b>\n\n"
            f"👤 User: {message.from_user.full_name}\n"
            f"🆔 User ID: <code>{uid}</code>\n"
            f"📦 Plan: {plan_name}\n"
            f"🧾 TXN: <code>{txn_id}</code>"
        ),
        parse_mode="HTML",
        reply_markup=admin_kb
    )
    bot.send_message(message.chat.id, "✅ Screenshot submitted! Please wait for admin approval.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_approve:"))
def handle_admin_approve(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Not authorized", show_alert=True)
        return
    parts = call.data.split(":")
    user_id = int(parts[1])
    plan_id = int(parts[2])
    txn_id = parts[3]
    plan = get_plan(plan_id)
    plan_name = plan["name"] if plan else "VIP Plan"

    try:
        bot.send_message(user_id, f"✅ <b>Payment Approved!</b>\nYour access for {plan_name} is active.", parse_mode="HTML")
    except Exception:
        pass

    screenshot_id = call.message.photo[-1].file_id if call.message.photo else None
    broadcast_caption = f"🎉 <b>SUCCESSFUL PURCHASE</b> 🎉\n\n📦 Plan: {plan_name}\n🟢 STATUS - UNLOCKED"

    for uid in get_all_users():
        try:
            if screenshot_id:
                bot.send_photo(uid, screenshot_id, caption=broadcast_caption, parse_mode="HTML", reply_markup=get_home_keyboard())
            else:
                bot.send_message(uid, broadcast_caption, parse_mode="HTML", reply_markup=get_home_keyboard())
        except Exception:
            pass

    bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=(call.message.caption or "") + "\n\n🟢 <b>APPROVED</b>", parse_mode="HTML")
    bot.answer_callback_query(call.id, "Approved successfully!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_reject:"))
def handle_admin_reject(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Not authorized", show_alert=True)
        return
    parts = call.data.split(":")
    user_id = int(parts[1])
    try:
        bot.send_message(user_id, "❌ <b>Payment Rejected.</b> Contact support if you think this is a mistake.", parse_mode="HTML")
    except Exception:
        pass
    bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=(call.message.caption or "") + "\n\n🔴 <b>REJECTED</b>", parse_mode="HTML")
    bot.answer_callback_query(call.id, "Rejected!")

def get_home_keyboard():
    kb = InlineKeyboardMarkup()
    for p in PLANS:
        if p.get("active"):
            kb.add(button(f"{p['name']} · ₹{p['price']}", callback_data=f"plan:{p['id']}"))
    return kb

# =========================================================
# ADMIN COMMANDS
# =========================================================

@bot.message_handler(commands=["upi"])
def cmd_set_upi(message):
    if message.from_user.id != ADMIN_ID: return
    msg = bot.send_message(message.chat.id, "✍️ <b>Send the new UPI ID:</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, process_new_upi)

def process_new_upi(message):
    if message.from_user.id != ADMIN_ID: return
    new_upi = message.text.strip()
    if "@" not in new_upi:
        bot.send_message(message.chat.id, "❌ Invalid UPI ID.")
        return
    set_current_upi(new_upi)
    bot.send_message(message.chat.id, f"✅ <b>UPI updated to:</b> <code>{new_upi}</code>", parse_mode="HTML")

@bot.message_handler(commands=["broadcast"])
def cmd_broadcast(message):
    if message.from_user.id != ADMIN_ID: return
    msg = bot.send_message(message.chat.id, "📢 <b>Send message to broadcast:</b>", parse_mode="HTML")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    if message.from_user.id != ADMIN_ID: return
    sent, failed = 0, 0
    for uid in get_all_users():
        try:
            bot.copy_message(chat_id=uid, from_chat_id=message.chat.id, message_id=message.message_id)
            sent += 1
        except Exception:
            failed += 1
    bot.send_message(message.chat.id, f"✅ <b>Broadcast complete.</b>\nSent: {sent}\nFailed: {failed}", parse_mode="HTML")

@bot.message_handler(commands=["getid"])
def cmd_get_id(message):
    if message.from_user.id != ADMIN_ID: return
    msg = bot.send_message(message.chat.id, "📹 Send any Photo or Video to get its File ID:")
    bot.register_next_step_handler(msg, process_get_id)

def process_get_id(message):
    if message.from_user.id != ADMIN_ID: return
    if message.photo:
        fid = message.photo[-1].file_id
        bot.send_message(message.chat.id, f"🖼 Photo File ID:\n<code>{fid}</code>", parse_mode="HTML")
    elif message.video:
        fid = message.video.file_id
        bot.send_message(message.chat.id, f"🎥 Video File ID:\n<code>{fid}</code>", parse_mode="HTML")

# =========================================================
# POLLING
# =========================================================

if __name__ == "__main__":
    log.info("🚀 Bot is starting...")
    bot.infinity_polling()
