import sqlite3
from flask import Flask
from threading import Thread
import telebot
from telebot import types

# --- سيرفر وهمي للحفاظ على مجانية Render ---
app = Flask("")


@app.route("/")
def home():
    return "Bot is Live!"


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


# ---------------- CONFIGURATION ----------------
TOKEN = "8826744317:AAEzlogirGNPyzg1vBRY538waG4XOINpJp8"
ADMIN_ID = 8192730669  # ضع أيدي حسابك برقم فقط
SHAM_CASH_ACCOUNT = "df910e178e027a6bfcae8b99b06b5384"  # رقم شام كاش

bot = telebot.TeleBot(TOKEN)

# ---------------- DATABASE SETUP ----------------
conn = sqlite3.connect("store.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
"""
)
conn.commit()


def get_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute(
            "INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0)
        )
        conn.commit()
        return 0


def update_balance(user_id, amount):
    get_balance(user_id)
    cursor.execute(
        "UPDATE users SET balance = balance + ? WHERE user_id = ?",
        (amount, user_id),
    )
    conn.commit()


# حالة المستخدمين لإدخال البيانات
user_states = {}


# 1. القائمة الرئيسية
@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.chat.id
    balance = get_balance(user_id)

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_pubg = types.InlineKeyboardButton(
        "🎮 شحن ببجي (PUBG)", callback_data="cat_pubg"
    )
    btn_ff = types.InlineKeyboardButton(
        "🔥 شحن فري فاير", callback_data="cat_ff"
    )
    btn_charge = types.InlineKeyboardButton(
        "💳 شحن الرصيد (شام كاش)", callback_data="charge_wallet"
    )
    btn_account = types.InlineKeyboardButton(
        "👤 حسابي", callback_data="my_account"
    )

    markup.add(btn_pubg, btn_ff)
    markup.add(btn_charge, btn_account)

    text = f"مرحباً بك في بوت الشحن! 🎮\n\nرصيدك الحالي: **{balance} ل.س**\nاختر من القائمة أدناه:"
    bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=markup)


# 2. معالجة الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.message.chat.id
    balance = get_balance(user_id)

    if call.data == "main_menu":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_welcome(call.message)

    elif call.data == "my_account":
        text = f"👤 **تفاصيل حسابك:**\n\n🆔 ID: `{user_id}`\n💰 الرصيد الحالي: **{balance} ل.س**"
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("🔙 العودة", callback_data="main_menu")
        )
        bot.edit_message_text(
            text,
            chat_id=user_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup,
        )

    elif call.data == "charge_wallet":
        text = (
            f"💳 **طريقة الشحن عبر شام كاش:**\n\n"
            f"1️⃣ قم بتحويل المبلغ إلى رقم شام كاش:\n`{SHAM_CASH_ACCOUNT}`\n\n"
            f"2️⃣ أرسل قيمة المبلغ المحول فقط في الرسالة التالية (أرقام فقط).\nمثال: `50000`"
        )
        user_states[user_id] = "WAITING_FOR_CHARGE"
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("🔙 إلغاء", callback_data="main_menu")
        )
        bot.edit_message_text(
            text,
            chat_id=user_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup,
        )

    elif call.data == "cat_pubg":
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                "60 شدة - 15,000 ل.س", callback_data="buy_pubg_60_15000"
            )
        )
        markup.add(
            types.InlineKeyboardButton(
                "325 شدة - 75,000 ل.س", callback_data="buy_pubg_325_75000"
            )
        )
        markup.add(
            types.InlineKeyboardButton("🔙 العودة", callback_data="main_menu")
        )
        bot.edit_message_text(
            "🎮 **اختر باقة PUBG Mobile:**",
            chat_id=user_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup,
        )

    elif call.data == "cat_ff":
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                "110 جوهرة - 12,000 ل.س", callback_data="buy_ff_110_12000"
            )
        )
        markup.add(
            types.InlineKeyboardButton(
                "530 جوهرة - 55,000 ل.س", callback_data="buy_ff_530_55000"
            )
        )
        markup.add(
            types.InlineKeyboardButton("🔙 العودة", callback_data="main_menu")
        )
        bot.edit_message_text(
            "🔥 **اختر باقة Free Fire:**",
            chat_id=user_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup,
        )

    elif call.data.startswith("buy_"):
        _, game, item, price = call.data.split("_")
        price = int(price)

        if balance < price:
            bot.answer_callback_query(
                call.id,
                "❌ رصيدك غير كافٍ! قم بشحن محفظتك أولاً.",
                show_alert=True,
            )
        else:
            user_states[user_id] = f"BUY_{game}_{item}_{price}"
            bot.send_message(
                user_id,
                f"📥 لشراء **{item}** بسعر **{price} ل.س**:\nالرجاء إرسال **Player ID (أيدي اللاعب)** الآن.",
            )

    # موافقة / رفض الأدمن
    elif call.data.startswith("adm_"):
        if call.from_user.id != ADMIN_ID:
            return

        _, action, target_id, amount = call.data.split("_")
        target_id, amount = int(target_id), int(amount)

        if action == "app":
            update_balance(target_id, amount)
            bot.edit_message_text(
                call.message.text + f"\n\n✅ **تمت الموافقة وإضافة {amount} ل.س.**",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )
            bot.send_message(
                target_id,
                f"🎉 تمت الموافقة على شحن حسابك بمبلغ {amount} ل.س بنجاح!",
            )
        elif action == "rej":
            bot.edit_message_text(
                call.message.text + f"\n\n❌ **تم رفض الطلب.**",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )
            bot.send_message(
                target_id, f"❌ عذراً، تم رفض طلب الشحن بمبلغ {amount} ل.س."
            )


# 3. استقبال النصوص (طلب الشحن أو Player ID)
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.chat.id
    state = user_states.get(user_id)

    if state == "WAITING_FOR_CHARGE":
        if message.text.isdigit():
            amount = int(message.text)
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(
                    "✅ قبول", callback_data=f"adm_app_{user_id}_{amount}"
                ),
                types.InlineKeyboardButton(
                    "❌ رفض", callback_data=f"adm_rej_{user_id}_{amount}"
                ),
            )

            bot.send_message(
                ADMIN_ID,
                f"📥 **طلب شحن جديد (شام كاش)!**\n\n👤 المستخدم: {message.from_user.first_name}\n🆔 ID: `{user_id}`\n💰 المبلغ: **{amount} ل.س**",
                parse_mode="Markdown",
                reply_markup=markup,
            )
            bot.reply_to(
                message,
                "⏳ تم إرسال طلب الشحن للإدارة، سيتم إضافة الرصيد فور التحقق.",
            )
            user_states[user_id] = None
        else:
            bot.reply_to(message, "❌ يرجى كتابة الأرقام فقط بدون حروف.")

    elif state and state.startswith("BUY_"):
        _, game, item, price = state.split("_")
        price = int(price)
        player_id = message.text

        # خصم الرصيد
        update_balance(user_id, -price)

        # إرسال للآدمين
        bot.send_message(
            ADMIN_ID,
            f"🛒 **طلب شراء لعبة جديد!**\n\n👤 الزبون: {message.from_user.first_name}\n🆔 ID الزبون: `{user_id}`\n📦 الطلب: **{game} - {item}**\n🎯 Player ID اللعبة: `{player_id}`",
            parse_mode="Markdown",
        )

        bot.reply_to(
            message,
            f"✅ تم خصم {price} ل.س وإرسال طلبك للآدمين بنجاح!\nسيتم الشحن للأيدي: `{player_id}` أسرع وقت.",
            parse_mode="Markdown",
        )
        user_states[user_id] = None


# تشغيل السيرفر والبوت
if __name__ == "__main__":
    keep_alive()  # لضمان بقائه يعمل على Render
    bot.infinity_polling()
