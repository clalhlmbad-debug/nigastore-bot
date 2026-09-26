from flask import Flask
import os
import threading
import sqlite3
import telebot
from telebot import types

# ================= الإعدادات =================

TOKEN = os.getenv("BOT_TOKEN", "8826744317:AAEzlogirGNPyzg1vBRY538waG4XOINpJp8")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8192730669"))
SHAM_CASH_ACCOUNT = os.getenv("SHAM_CASH"," d1f48dff44e504323052c3b6533cd296")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN غير موجود")

if not ADMIN_ID:
    raise RuntimeError("ADMIN_ID غير موجود")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ================= سيرفر Render =================

app = Flask(__name__)

@app.route("/")
def home():
    return "NigaStore Bot is running"

@app.route("/health")
def health():
    return {"status": "ok"}

def run_web():
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    threading.Thread(target=run_web, daemon=True).start()

# ================= قاعدة البيانات SQLite =================

DB_FILE = "niga_store.db"

def db():
    conn = sqlite3.connect(DB_FILE, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS topups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tx_id TEXT NOT NULL,
            amount INTEGER,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game TEXT NOT NULL,
            item TEXT NOT NULL,
            price INTEGER NOT NULL,
            player_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= المستخدمين =================

def ensure_user(user_id):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO users(user_id)
        VALUES(?)
    """, (user_id,))

    conn.commit()
    conn.close()


def get_balance(user_id):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT balance FROM users WHERE user_id=?",
        (user_id,)
    )

    row = cur.fetchone()
    balance = row["balance"] if row else 0

    conn.close()

    return balance


def add_balance(user_id, amount):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET balance = balance + ?
        WHERE user_id = ?
    """, (amount, user_id))

    conn.commit()
    conn.close()


def deduct_balance(user_id, amount):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET balance = balance - ?
        WHERE user_id = ?
        AND balance >= ?
    """, (amount, user_id, amount))

    result = cur.rowcount == 1

    if result:
        conn.commit()
    else:
        conn.rollback()

    conn.close()

    return result


# ================= الباقات =================

PUBG = [
    ("60 UC", 130),
    ("325 UC", 680),
    ("660 UC", 1350),
    ("1800 UC", 3500),
]

FREE_FIRE = [
    ("110 Diamonds", 110),
    ("530 Diamonds", 500),
    ("1080 Diamonds", 980),
    ("2200 Diamonds", 1950),
]

states = {}


# ================= القائمة الرئيسية =================

def main_menu(user_id):

    balance = get_balance(user_id)

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        types.InlineKeyboardButton(
            "🎮 PUBG Mobile",
            callback_data="game:pubg"
        ),
        types.InlineKeyboardButton(
            "🔥 Free Fire",
            callback_data="game:ff"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "💳 شحن الرصيد",
            callback_data="wallet"
        ),
        types.InlineKeyboardButton(
            "👤 حسابي",
            callback_data="account"
        )
    )

    text = (
        "🎮 <b>مرحباً بك في NigaStore</b>\n\n"
        f"💰 رصيدك الحالي: <b>{balance:,} ل.س</b>\n\n"
        "اختر الخدمة:"
    )

    return text, keyboard


def show_main(user_id):

    text, keyboard = main_menu(user_id)

    bot.send_message(
        user_id,
        text,
        reply_markup=keyboard
    )


# ================= /start =================

@bot.message_handler(commands=["start", "menu"])
def start(message):

    ensure_user(message.chat.id)

    show_main(message.chat.id)


# ================= الأزرار =================

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):

    user_id = call.from_user.id
    data = call.data

    try:

        # القائمة
        if data == "main":

            states.pop(user_id, None)

            text, keyboard = main_menu(user_id)

            bot.edit_message_text(
                text,
                chat_id=user_id,
                message_id=call.message.message_id,
                reply_markup=keyboard
            )

        # الحساب
        elif data == "account":

            balance = get_balance(user_id)

            keyboard = types.InlineKeyboardMarkup()

            keyboard.add(
                types.InlineKeyboardButton(
                    "📜 سجل الطلبات",
                    callback_data="history"
                )
            )

            keyboard.add(
                types.InlineKeyboardButton(
                    "🔙 القائمة",
                    callback_data="main"
                )
            )

            text = (
                "👤 <b>حسابك</b>\n\n"
                f"🆔 ID: <code>{user_id}</code>\n"
                f"💰 الرصيد: <b>{balance:,} ل.س</b>"
            )

            bot.edit_message_text(
                text,
                chat_id=user_id,
                message_id=call.message.message_id,
                reply_markup=keyboard
            )

        # سجل الطلبات
        elif data == "history":

            conn = db()
            cur = conn.cursor()

            cur.execute("""
                SELECT id, game, item, price, player_id, status
                FROM orders
                WHERE user_id=?
                ORDER BY id DESC
                LIMIT 10
            """, (user_id,))

            rows = cur.fetchall()

            conn.close()

            if not rows:

                text = (
                    "📜 <b>سجل الطلبات</b>\n\n"
                    "لا يوجد لديك طلبات حتى الآن."
                )

            else:

                status_names = {
                    "pending": "⏳ بانتظار التأكيد",
                    "paid_pending": "🔄 قيد التنفيذ",
                    "completed": "✅ مكتمل",
                    "refunded": "↩️ مسترجع"
                }

                lines = ["📜 <b>آخر الطلبات</b>\n"]

                for row in rows:

                    status = status_names.get(
                        row["status"],
                        row["status"]
                    )

                    lines.append(
                        f"🔢 #{row['id']}\n"
                        f"🎮 {row['game']}\n"
                        f"📦 {row['item']}\n"
                        f"💰 {row['price']:,} ل.س\n"
                        f"👤 <code>{row['player_id']}</code>\n"
                        f"{status}\n"
                    )

                text = "\n".join(lines)

            keyboard = types.InlineKeyboardMarkup()

            keyboard.add(
                types.InlineKeyboardButton(
                    "🔙 القائمة",
                    callback_data="main"
                )
            )

            bot.edit_message_text(
                text,
                chat_id=user_id,
                message_id=call.message.message_id,
                reply_markup=keyboard
            )

        # PUBG
        elif data == "game:pubg":

            show_products(
                user_id,
                "PUBG",
                PUBG,
                call.message.message_id
            )

        # Free Fire
        elif data == "game:ff":

            show_products(
                user_id,
                "Free Fire",
                FREE_FIRE,
                call.message.message_id
            )

        # شحن الرصيد
        elif data == "wallet":

            states[user_id] = {
                "type": "wallet_tx"
            }

            keyboard = types.InlineKeyboardMarkup()

            keyboard.add(
                types.InlineKeyboardButton(
                    "❌ إلغاء",
                    callback_data="main"
                )
            )

            text = (
                "💳 <b>شحن الرصيد عبر شام كاش</b>\n\n"
                f"حوّل المبلغ إلى:\n"
                f"<code>{SHAM_CASH_ACCOUNT}</code>\n\n"
                "بعد التحويل أرسل رقم العملية."
            )

            bot.edit_message_text(
                text,
                chat_id=user_id,
                message_id=call.message.message_id,
                reply_markup=keyboard
            )

        # شراء
        elif data.startswith("buy:"):

            _, game, index = data.split(":")

            products = PUBG if game == "PUBG" else FREE_FIRE

            item, price = products[int(index)]

            balance = get_balance(user_id)

            if balance < price:

                bot.answer_callback_query(
                    call.id,
                    f"❌ الرصيد غير كافٍ. السعر {price:,} ل.س",
                    show_alert=True
                )

                return

            states[user_id] = {
                "type": "player_id",
                "game": game,
                "item": item,
                "price": price
            }

            bot.send_message(
                user_id,
                f"📦 <b>{item}</b>\n"
                f"💰 السعر: <b>{price:,} ل.س</b>\n\n"
                "أرسل Player ID الخاص بك:"
            )

        # تأكيد الطلب
        elif data.startswith("confirm:"):

            order_id = int(data.split(":")[1])

            conn = db()
            cur = conn.cursor()

            cur.execute("""
                SELECT user_id, game, item, price, player_id
                FROM orders
                WHERE id=?
                AND user_id=?
                AND status='pending'
            """, (order_id, user_id))

            order = cur.fetchone()

            conn.close()

            if not order:

                bot.answer_callback_query(
                    call.id,
                    "❌ الطلب غير موجود",
                    show_alert=True
                )

                return

            price = order["price"]

            if not deduct_balance(user_id, price):

                bot.answer_callback_query(
                    call.id,
                    "❌ الرصيد غير كافٍ",
                    show_alert=True
                )

                return

            conn = db()
            cur = conn.cursor()

            cur.execute("""
                UPDATE orders
                SET status='paid_pending'
                WHERE id=?
            """, (order_id,))

            conn.commit()
            conn.close()

            keyboard = types.InlineKeyboardMarkup(row_width=2)

            keyboard.add(
                types.InlineKeyboardButton(
                    "✅ تم الشحن",
                    callback_data=f"done:{order_id}"
                ),
                types.InlineKeyboardButton(
                    "↩️ إرجاع المبلغ",
                    callback_data=f"refund:{order_id}"
                )
            )

            bot.send_message(
                ADMIN_ID,
                "🛒 <b>طلب شحن جديد</b>\n\n"
                f"🔢 الطلب: <b>#{order_id}</b>\n"
                f"👤 العميل: <code>{user_id}</code>\n"
                f"🎮 اللعبة: {order['game']}\n"
                f"📦 الباقة: {order['item']}\n"
                f"💰 السعر: {price:,} ل.س\n"
                f"👤 Player ID: <code>{order['player_id']}</code>",
                reply_markup=keyboard
            )

            bot.edit_message_text(
                f"⏳ تم إرسال طلبك #{order_id} للإدارة.\n\n"
                f"تم خصم {price:,} ل.س من رصيدك مؤقتاً.",
                chat_id=user_id,
                message_id=call.message.message_id
            )

        # إلغاء الطلب
        elif data.startswith("cancel:"):

            order_id = int(data.split(":")[1])

            conn = db()
            cur = conn.cursor()

            cur.execute("""
                DELETE FROM orders
                WHERE id=?
                AND user_id=?
                AND status='pending'
            """, (order_id, user_id))

            conn.commit()
            conn.close()

            bot.edit_message_text(
                "❌ تم إلغاء الطلب.",
                chat_id=user_id,
                message_id=call.message.message_id
            )

        # تم الشحن
        elif data.startswith("done:"):

            if user_id != ADMIN_ID:
                return

            order_id = int(data.split(":")[1])

            conn = db()
            cur = conn.cursor()

            cur.execute("""
                SELECT user_id, item, player_id
                FROM orders
                WHERE id=?
                AND status='paid_pending'
            """, (order_id,))

            order = cur.fetchone()

            if not order:

                conn.close()
                return

            cur.execute("""
                UPDATE orders
                SET status='completed',
                    reviewed_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (order_id,))

            conn.commit()
            conn.close()

            bot.send_message(
                order["user_id"],
                "🎉 <b>تم تنفيذ طلبك بنجاح!</b>\n\n"
                f"📦 {order['item']}\n"
                f"👤 Player ID: <code>{order['player_id']}</code>\n"
                f"🔢 الطلب: #{order_id}"
            )

            bot.edit_message_text(
                call.message.text +
                "\n\n✅ <b>تم تسجيل الشحن.</b>",
                chat_id=ADMIN_ID,
                message_id=call.message.message_id
            )

        # إرجاع المبلغ
        elif data.startswith("refund:"):

            if user_id != ADMIN_ID:
                return

            order_id = int(data.split(":")[1])

            conn = db()
            cur = conn.cursor()

            cur.execute("""
                SELECT user_id, price
                FROM orders
                WHERE id=?
                AND status='paid_pending'
            """, (order_id,))

            order = cur.fetchone()

            if not order:

                conn.close()
                return

            cur.execute("""
                UPDATE users
                SET balance=balance+?
                WHERE user_id=?
            """, (order["price"], order["user_id"]))

            cur.execute("""
                UPDATE orders
                SET status='refunded',
                    reviewed_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (order_id,))

            conn.commit()
            conn.close()

            bot.send_message(
                order["user_id"],
                f"↩️ تم إرجاع "
                f"<b>{order['price']:,} ل.س</b> "
                f"إلى رصيدك.\n"
                f"الطلب #{order_id}"
            )

            bot.edit_message_text(
                call.message.text +
                "\n\n↩️ <b>تم إرجاع المبلغ.</b>",
                chat_id=ADMIN_ID,
                message_id=call.message.message_id
            )

        # قبول شحن الرصيد
        elif data.startswith("topup_ok:"):

            if user_id != ADMIN_ID:
                return

            topup_id = int(data.split(":")[1])

            conn = db()
            cur = conn.cursor()

            cur.execute("""
                SELECT user_id, amount
                FROM topups
                WHERE id=?
                AND status='pending'
            """, (topup_id,))

            topup = cur.fetchone()

            if not topup:

                conn.close()
                return

            cur.execute("""
                UPDATE users
                SET balance=balance+?
                WHERE user_id=?
            """, (topup["amount"], topup["user_id"]))

            cur.execute("""
                UPDATE topups
                SET status='approved',
                    reviewed_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (topup_id,))

            conn.commit()
            conn.close()

            bot.send_message(
                topup["user_id"],
                f"✅ تم قبول شحن الرصيد.\n\n"
                f"💰 تمت إضافة "
                f"<b>{topup['amount']:,} ل.س</b> "
                f"إلى رصيدك."
            )

            bot.edit_message_text(
                call.message.text +
                "\n\n✅ <b>تم قبول الشحن.</b>",
                chat_id=ADMIN_ID,
                message_id=call.message.message_id
            )

        # رفض شحن الرصيد
        elif data.startswith("topup_no:"):

            if user_id != ADMIN_ID:
                return

            topup_id = int(data.split(":")[1])

            conn = db()
            cur = conn.cursor()

            cur.execute("""
                SELECT user_id
                FROM topups
                WHERE id=?
                AND status='pending'
            """, (topup_id,))

            topup = cur.fetchone()

            if not topup:

                conn.close()
                return

            cur.execute("""
                UPDATE topups
                SET status='rejected',
                    reviewed_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (topup_id,))

            conn.commit()
            conn.close()

            bot.send_message(
                topup["user_id"],
                "❌ تم رفض طلب شحن الرصيد."
            )

            bot.edit_message_text(
                call.message.text +
                "\n\n❌ <b>تم رفض الشحن.</b>",
                chat_id=ADMIN_ID,
                message_id=call.message.message_id
            )

        bot.answer_callback_query(call.id)

    except Exception as error:

        print("ERROR:", error)

        try:
            bot.answer_callback_query(
                call.id,
                "حدث خطأ، حاول مرة أخرى.",
                show_alert=True
            )
        except:
            pass


# ================= عرض الباقات =================

def show_products(user_id, game, products, message_id):

    keyboard = types.InlineKeyboardMarkup()

    game_code = "PUBG" if game == "PUBG" else "FF"

    for index, (item, price) in enumerate(products):

        keyboard.add(
            types.InlineKeyboardButton(
                f"{item} — {price:,} ل.س",
                callback_data=f"buy:{game_code}:{index}"
            )
        )

    keyboard.add(
        types.InlineKeyboardButton(
            "🔙 القائمة",
            callback_data="main"
        )
    )

    bot.edit_message_text(
        f"🎮 اختر باقة <b>{game}</b>:",
        chat_id=user_id,
        message_id=message_id,
        reply_markup=keyboard
    )


# ================= استقبال الرسائل =================

@bot.message_handler(
    func=lambda message: True,
    content_types=["text"]
)
def messages(message):

    user_id = message.from_user.id

    state = states.get(user_id)

    if not state:

        ensure_user(user_id)

        show_main(user_id)

        return

    text = message.text.strip()

    # رقم عملية شام كاش
    if state["type"] == "wallet_tx":

        states[user_id] = {
            "type": "wallet_amount",
            "tx_id": text
        }

        bot.send_message(
            user_id,
            "💰 أرسل الآن مبلغ التحويل بالليرة السورية، أرقام فقط."
        )

        return

    # مبلغ التحويل
    if state["type"] == "wallet_amount":

        if not text.isdigit():

            bot.send_message(
                user_id,
                "❌ أرسل المبلغ بالأرقام فقط."
            )

            return

        amount = int(text)

        if amount <= 0:

            bot.send_message(
                user_id,
                "❌ المبلغ يجب أن يكون أكبر من صفر."
            )

            return

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO topups(user_id, tx_id, amount)
            VALUES(?,?,?)
