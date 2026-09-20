import telebot
from telebot import types
import os
import sqlite3
from flask import Flask
from threading import Thread

# --- إعدادات سيرفر الحفاظ على مجانية الـ Render ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Live!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعدادات البوت الأساسية المتكاملة ---
BOT_TOKEN = '8826744317:AAEY8S9xK4B4dXA3-kN2J6JyBF3ng701Ipg'
ADMIN_ID = 8192730669
SHAM_CASH_WALLET = "df910e178e027a6bfcae8b99b06b5384"

bot = telebot.TeleBot(BOT_TOKEN)
user_sessions = {}

# --- إعداد وإنشاء قاعدة البيانات لحفظ الطلبات بصورها ---
def init_db():
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            user_id INTEGER,
            package_name TEXT,
            player_id TEXT,
            photo_id TEXT,
            status TEXT DEFAULT 'PENDING'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# قائمة الباقات
PACKAGES = {
    'pubg_b1': {'game': '🎮 ببجي موبايل', 'name': '60 شدة (UC)', 'price': '15,000 ل.س'},
    'pubg_b2': {'game': '🎮 ببجي موبايل', 'name': '325 شدة (UC)', 'price': '65,000 ل.س'},
    'pubg_b3': {'game': '🎮 ببجي موبايل', 'name': '660 شدة (UC)', 'price': '125,000 ل.س'},
    'ff_f1': {'game': '💎 فري فاير', 'name': '100 جوهرة', 'price': '12,000 ل.س'},
    'ff_f2': {'game': '💎 فري فاير', 'name': '210 جوهرة', 'price': '24,000 ل.س'},
    'ff_f3': {'game': '💎 فري فاير', 'name': '530 جوهرة', 'price': '55,000 ل.س'}
}

# أمر البداية /start
@bot.message_handler(commands=['start'])
def start_message(message):
    uid = message.chat.id
    user_sessions[uid] = {} 
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_pubg = types.InlineKeyboardButton("🎮 شحن شدات ببجي (PUBG UC)", callback_data="show_pubg")
    btn_ff = types.InlineKeyboardButton("🔥 شحن جواهر فري فاير (Free Fire)", callback_data="show_freefire")
    markup.add(btn_pubg, btn_ff)
    
    welcome_text = (
        "⚡ **أهلاً بك في متجر شحن الألعاب الفوري المعتمد!** ⚡\n\n"
        "👇 **من فضلك اختر اللعبة التي ترغب في شحنها الآن:**"
    )
    bot.send_message(uid, welcome_text, parse_mode="Markdown", reply_markup=markup)

# معالجة ضغطات الأزرار واختيار الباقات
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.message.chat.id
    
    if call.data == "show_pubg":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, pkg in PACKAGES.items():
            if key.startswith('pubg_'):
                markup.add(types.InlineKeyboardButton(f"📦 {pkg['name']} ← {pkg['price']}", callback_data=f"select_{key}"))
        markup.add(types.InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data="go_home"))
        bot.edit_message_text(chat_id=uid, message_id=call.message.message_id, text="🛒 **باقات شدات ببجي موبايل:**", parse_mode="Markdown", reply_markup=markup)
        
    elif call.data == "show_freefire":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, pkg in PACKAGES.items():
            if key.startswith('ff_'):
                markup.add(types.InlineKeyboardButton(f"📦 {pkg['name']} ← {pkg['price']}", callback_data=f"select_{key}"))
        markup.add(types.InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data="go_home"))
        bot.edit_message_text(chat_id=uid, message_id=call.message.message_id, text="🛒 **باقات جواهر فري فاير:**", parse_mode="Markdown", reply_markup=markup)

    elif call.data == "go_home":
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_pubg = types.InlineKeyboardButton("🎮 شحن شدات ببجي (PUBG UC)", callback_data="show_pubg")
        btn_ff = types.InlineKeyboardButton("🔥 شحن جواهر فري فاير (Free Fire)", callback_data="show_freefire")
        markup.add(btn_pubg, btn_ff)
        bot.edit_message_text(chat_id=uid, message_id=call.message.message_id, text="⚡ **من فضلك اختر اللعبة التي ترغب في شحنها الآن:**", parse_mode="Markdown", reply_markup=markup)

    elif call.data.startswith("select_"):
        pkg_id = call.data.replace("select_", "")
        user_sessions[uid] = {'package_key': pkg_id}
        msg = bot.send_message(uid, "🆔 **من فضلك، قم بكتابة معرف اللاعب الخاص بك (Player ID) في اللعبة:**")
        bot.register_next_step_handler(msg, process_player_id)

    elif call.data.startswith("approve_"):
        order_id = call.data.replace("approve_", "")
        conn = sqlite3.connect('orders.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, package_name, player_id, status FROM orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        if row and row[3] == 'PENDING':
            cursor.execute("UPDATE orders SET status = 'APPROVED' WHERE order_id = ?", (order_id,))
            conn.commit()
            bot.send_message(row[0], f"🎉 **تهانينا!** تم شحن باقة **({row[1]})** لحساب الـ ID: `{row[2]}` بنجاح.", parse_mode="Markdown")
            bot.edit_message_text(chat_id=ADMIN_ID, message_id=call.message.message_id, text=f"🟢 **تم شحن طلب اللاعب:** `{row[2]}` بنجاح.")
        conn.close()

    elif call.data.startswith("reject_"):
        order_id = call.data.replace("reject_", "")
        conn = sqlite3.connect('orders.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, package_name, player_id, status FROM orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        if row and row[3] == 'PENDING':
            cursor.execute("UPDATE orders SET status = 'REJECTED' WHERE order_id = ?", (order_id,))
            conn.commit()
            bot.send_message(row[0], "❌ **نعتذر منك!** تم رفض طلب الشحن الخاص بك نظراً لعدم صحة التحويل أو عدم وضوح الإيصال.", parse_mode="Markdown")
            bot.edit_message_text(chat_id=ADMIN_ID, message_id=call.message.message_id, text=f"🔴 **تم رفض طلب اللاعب:** `{row[2]}`.")
        conn.close()

def process_player_id(message):
    uid = message.chat.id
    player_id = message.text
    if uid not in user_sessions or 'package_key' not in user_sessions[uid]:
        bot.send_message(uid, "⚠️ حدث خطأ، أرسل /start")
        return
    user_sessions[uid]['player_id'] = player_id
    pkg = PACKAGES[user_sessions[uid]['package_key']]
    
    payment_instruction = (
        f"💳 **خطوة الدفع الفوري (شام كاش):**\n\n"
        f"لإتمام شحن باقة **{pkg['name']}**:\n"
        f"💵 يرجى تحويل: **{pkg['price']}** إلى المحفظة التالية:\n\n"
        f"`{SHAM_CASH_WALLET}`\n\n"
        f"📸 بعد التحويل، **أرسل لقطة شاشة لإيصال التحويل (صورة) هنا:**"
    )
    msg = bot.send_message(uid, payment_instruction, parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_payment_photo)

def process_payment_photo(message):
    uid = message.chat.id
    if message.content_type != 'photo':
        msg = bot.send_message(uid, "⚠️ يرجى إرسال صورة إيصال الدفع:")
        bot.register_next_step_handler(msg, process_payment_photo)
        return

    pkg = PACKAGES[user_sessions[uid]['package_key']]
    player_id = user_sessions[uid]['player_id']
    photo_id = message.photo[-1].file_id
    order_id = f"{uid}_{message.message_id}"
    
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO orders (order_id, user_id, package_name, player_id, photo_id) VALUES (?, ?, ?, ?, ?)",
                   (order_id, uid, pkg['name'], player_id, photo_id))
    conn.commit()
    conn.close()
    
    admin_markup = types.InlineKeyboardMarkup(row_width=2)
    admin_markup.add(
        types.InlineKeyboardButton("✅ قبول وشحن", callback_data=f"approve_{order_id}"),
        types.InlineKeyboardButton("❌ رفض الطلب", callback_data=f"reject_{order_id}")
    )
    
    admin_alert = (
        f"🔔 **طلب شحن جديد!**\n\n"
        f"🎮 **اللعبة:** {pkg['game']}\n"
        f"📦 **الباقة:** {pkg['name']}\n"
        f"🆔 **آيدي اللاعب:** `{player_id}`\n"
        f"👤 **المشتري:** {message.from_user.first_name} (@{message.from_user.username or 'بدون_يوزر'})"
    )
    bot.send_photo(ADMIN_ID, photo_id, caption=admin_alert, parse_mode="Markdown", reply_markup=admin_markup)
    bot.send_message(uid, "⏳ **تم رفع الطلب بنجاح وجاري مراجعته من قِبل الإدارة!**")

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling()
