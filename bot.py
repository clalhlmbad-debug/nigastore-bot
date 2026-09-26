from datetime import datetime
from flask import Flask
import os
import threading
import telebot
from telebot import types
import psycopg2
from psycopg2.extras import RealDictCursor

# ================= الإعدادات =================

TOKEN = os.getenv("BOT_TOKEN", "8826744317:AAEzlogirGNPyzg1vBRY538waG4XOINpJp8")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8192730669"))
SHAM_CASH_ACCOUNT = os.getenv("SHAM_CASH", "d1f48dff44e504323052c3b6533cd296")
DATABASE_URL = os.getenv("DATABASE_URL", "Postgresql://postgres:[Ahmad0998211716]@db.igbuukbgiepmmntazhlm.supabase.co:5432/postgres")

if not TOKEN:
    raise RuntimeError("8826744317:AAEzlogirGNPyzg1vBRY538waG4XOINpJp8")

if not ADMIN_ID:
    raise RuntimeError("8192730669")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL غير موجود")

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

# ================= قاعدة البيانات =================

def db():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            balance BIGINT NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS topups (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            tx_id TEXT NOT NULL,
            amount BIGINT,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            reviewed_at TIMESTAMPTZ
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            game TEXT NOT NULL,
            item TEXT NOT NULL,
            price BIGINT NOT NULL,
            player_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            reviewed_at TIMESTAMPTZ
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

init_db()

# ================= المستخدمين =================

def ensure_user(user_id):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users(user_id)
        VALUES(%s)
        ON CONFLICT(user_id) DO NOTHING
    """, (user_id,))

    conn.commit()
    cur.close()
    conn.close()


def get_balance(user_id):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT balance FROM users WHERE user_id=%s",
        (user_id,)
    )

    balance = cur.fetchone()[0]

    cur.close()
    conn.close()

    return balance


def add_balance(user_id, amount):
    ensure_user(user_id)

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET balance = balance + %s
        WHERE user_id = %s
    """, (amount, user_id))

    conn.commit()
    cur.close()
    conn.close()


def deduct_balance(user_id, amount):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET balance = balance - %s
        WHERE user_id = %s
        AND balance >= %s
        RETURNING balance
    """, (amount, user_id, amount))

    row = cur.fetchone()

    if row:
        conn.commit()
        result = True
    else:
        conn.rollback()
        result = False

    cur.close()
    conn.close()

    return result


# ================= الباقات =================

PUBG = [
    ("60 UC", 13500),
    ("325 UC", 68000),
    ("660 UC", 135000),
    ("1800 UC", 350000),
]

FREE_FIRE = [
    ("110 Diamonds", 11000),
    ("530 Diamonds", 50000),
    ("1080 Diamonds", 98000),
    ("2200 Diamonds", 195000),
]

# حالات المستخدم المؤقتة
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

        # العودة للقائمة
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

        # شراء باقة
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
                WHERE id=%s
                AND user_id=%s
                AND status='pending'
            """, (order_id, user_id))

            order = cur.fetchone()

            cur.close()
            conn.close()

            if not order:

                bot.answer_callback_query(
                    call.id,
                    "❌ الطلب غير موجود",
                    show_alert=True
                )

                return

            price = order[3]

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
                WHERE id=%s
            """, (order_id,))

            conn.commit()

            cur.close()
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
                f"🎮 اللعبة: {order[1]}\n"
                f"📦 الباقة: {order[2]}\n"
                f"💰 السعر: {price:,} ل.س\n"
                f"👤 Player ID: <code>{order[4]}</code>",
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
                WHERE id=%s
                AND user_id=%s
                AND status='pending'
            """, (order_id, user_id))

            conn.commit()

            cur.close()
            conn.close()

            bot.edit_message_text(
                "❌ تم إلغاء الطلب.",
                chat_id=user_id,
                message_id=call.message.message_id
            )

        # ================= الأدمن =================

        elif data.startswith("done:"):

            if user_id != ADMIN_ID:
                return

            order_id = int(data.split(":")[1])

            conn = db()
            cur = conn.cursor()

            cur.execute("""
                SELECT user_id, item, player_id
                FROM orders
                WHERE id=%s
                AND status='paid_pending'
            """, (order_id,))

            order = cur.fetchone()

            if not order:
                conn.rollback()
                cur.close()
                conn.close()
                return

            cur.execute("""
                UPDATE orders
                SET status='completed',
                    reviewed_at=NOW()
                WHERE id=%s
            """, (order_id,))

            conn.commit()

            cur.close()
            conn.close()

            bot.send_message(
                order[0],
                "🎉 <b>تم تنفيذ طلبك بنجاح!</b>\n\n"
                f"📦 {order[1]}\n"
                f"👤 Player ID: <code>{order[2]}</code>\n"
                f"🔢 الطلب: #{order_id}"
            )

            bot.edit_message_text(
                call.message.text + "\n\n✅ <b>تم تسجيل الشحن.</b>",
                chat_id=ADMIN_ID,
                message_id=call.message.message_id
            )

        # إرجاع مبلغ الطلب
        elif data.startswith("refund:"):

            if user_id != ADMIN_ID:
                return

            order_id = int(data.split(":")[1])

            conn = db()
            cur = conn.cursor()

            cur.execute("""
                SELECT user_id, price
                FROM orders
                WHERE id=%s
                AND status='paid_pending'
            """, (order_id,))

            order = cur.fetchone()

            if not order:
                conn.rollback()
                cur.close()
                conn.close()
                return

            cur.execute("""
                UPDATE users
                SET balance=balance+%s
                WHERE user_id=%s
            """, (order[1], order[0]))

            cur.execute("""
                UPDATE orders
                SET status='refunded',
                    reviewed_at=NOW()
                WHERE id=%s
            """, (order_id,))

            conn.commit()

            cur.close()
            conn.close()

            bot.send_message(
                order[0],
                f"↩️ تم إرجاع <b>{order[1]:,} ل.س</b> إلى رصيدك.\n"
                f"الطلب #{order_id}"
            )

            bot.edit_message_text(
                call.message.text + "\n\n↩️ <b>تم إرجاع المبلغ.</b>",
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

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO topups(user_id, tx_id, amount)
            VALUES(%s,%s,%s)
            RETURNING id
        """, (
            user_id,
            state["tx_id"],
            amount
        ))

        topup_id = cur.fetchone()[0]

        conn.commit()

        cur.close()
        conn.close()

        states.pop(user_id, None)

        keyboard = types.InlineKeyboardMarkup(row_width=2)

        keyboard.add(
            types.InlineKeyboardButton(
                "✅ قبول",
                callback_data=f"topup_ok:{topup_id}"
            ),
            types.InlineKeyboardButton(
                "❌ رفض",
                callback_data=f"topup_no:{topup_id}"
            )
        )

        bot.send_message(
            ADMIN_ID,
            "💳 <b>طلب شحن رصيد</b>\n\n"
            f"🔢 الطلب: #{topup_id}\n"
            f"👤 المستخدم: <code>{user_id}</code>\n"
            f"🧾 رقم العملية: <code>{state['tx_id']}</code>\n"
            f"💰 المبلغ: <b>{amount:,} ل.س</b>\n\n"
            "تحقق من شام كاش قبل الموافقة.",
            reply_markup=keyboard
        )

        bot.send_message(
            user_id,
            "⏳ تم إرسال طلب شحن الرصيد للإدارة."
        )

        return

    # Player ID
    if state["type"] == "player_id":

        player_id = text

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO orders(
                user_id,
                game,
                item,
                price,
                player_id
            )
            VALUES(%s,%s,%s,%s,%s)
            RETURNING id
        """, (
            user_id,
            state["game"],
            state["item"],
            state["price"],
            player_id
        ))

        order_id = cur.fetchone()[0]

        conn.commit()

        cur.close()
        conn.close()

        states.pop(user_id, None)

        keyboard = types.InlineKeyboardMarkup(row_width=2)

        keyboard.add(
            types.InlineKeyboardButton(
                "✅ تأكيد",
                callback_data=f"confirm:{order_id}"
            ),
            types.InlineKeyboardButton(
                "❌ إلغاء",
                callback_data=f"cancel:{order_id}"
            )
        )

        bot.send_message(
            user_id,
            "🛒 <b>تأكيد الطلب</b>\n\n"
            f"🎮 اللعبة: {state['game']}\n"
            f"📦 الباقة: {state['item']}\n"
            f"💰 السعر: {state['price']:,} ل.س\n"
            f"👤 Player ID: <code>{player_id}</code>\n\n"
            "هل تريد تأكيد الطلب؟",
            reply_markup=keyboard
        )


# ================= التشغيل =================

if __name__ == "__main__":

    keep_alive()

    print("NigaStore Bot Started")

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    )
