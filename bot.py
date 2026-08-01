import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# --- تشغيل سيرفر وهمي للحفاظ على مجانية Render ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Live and Running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- الإعدادات الأساسية للبوت ---
TOKEN = "8826744317:AAFho5aCppPS1we_4kkp4Rz1SX6fh32K-Y8"
ADMIN_ID = 8192730669
SHAM_CASH_ACCOUNT = "df910e178e027a6bfcae8b9b06b5384"
EXCHANGE_RATE = 145

bot = telebot.TeleBot(TOKEN)
user_orders = {}
ORDERS_FILE = "all_orders.txt"

PRICES = {
    "buy_pubg_60": 0.92,
    "buy_pubg_325": 4.59,
    "buy_pubg_660": 9.19,
    "buy_ff_110": 0.98,
    "buy_ff_231": 1.96
}

def save_order_to_file(order_details):
    with open(ORDERS_FILE, "a", encoding="utf-8") as f:
        f.write(order_details + "\n" + "-"*30 + "\n")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_games = types.InlineKeyboardButton("🎮 قسم الألعاب", callback_data="games_menu")
    btn_support = types.InlineKeyboardButton("👨‍💻 الدعم الفني", callback_data="support_menu")
    markup.add(btn_games, btn_support)
    if message.chat.id == ADMIN_ID:
        btn_admin = types.InlineKeyboardButton("📋 جميع الطلبات", callback_data="admin_view_orders")
        markup.add(btn_admin)
    welcome_text = f"👋 أهلاً بك في بوت Niga Store!\n\n📌 سعر الصرف الحالي: 1$ = {EXCHANGE_RATE} ل.س\n\n🤖 اختر القسم المناسب:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "games_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📱 ببجي موبايل", callback_data="pubg_info"),
            types.InlineKeyboardButton("🔥 فري فاير", callback_data="ff_info"),
            types.InlineKeyboardButton("🔙 العودة", callback_data="main_menu")
        )
        bot.edit_message_text("🎮 اختر لعبتك المفضلة:", chat_id, call.message.message_id, reply_markup=markup)
    elif call.data == "pubg_info":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"📦 60 UC - {round(0.92 * EXCHANGE_RATE)} ل.س", callback_data="buy_pubg_60"),
            types.InlineKeyboardButton(f"📦 325 UC - {round(4.59 * EXCHANGE_RATE)} ل.س", callback_data="buy_pubg_325"),
            types.InlineKeyboardButton(f"📦 660 UC - {round(9.19 * EXCHANGE_RATE)} ل.س", callback_data="buy_pubg_660"),
            types.InlineKeyboardButton("🔙 العودة", callback_data="games_menu")
        )
        bot.edit_message_text("📱 اختر الفئة المناسبة لببجي:", chat_id, call.message.message_id, reply_markup=markup)
    elif call.data == "ff_info":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"💎 110 Gems - {round(0.98 * EXCHANGE_RATE)} ل.س", callback_data="buy_ff_110"),
            types.InlineKeyboardButton(f"💎 231 Gems - {round(1.96 * EXCHANGE_RATE)} ل.س", callback_data="buy_ff_231"),
            types.InlineKeyboardButton("🔙 العودة", callback_data="games_menu")
        )
        bot.edit_message_text("🔥 اختر الفئة المناسبة لفري فاير:", chat_id, call.message.message_id, reply_markup=markup)
    elif call.data == "support_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("💬 تواصل مع المطور", url="https://t.me"),
            types.InlineKeyboardButton("🔙 العودة", callback_data="main_menu")
        )
        bot.edit_message_text("👨‍💻 للدعم الفني تواصل معنا عبر الزر أدناه:", chat_id, call.message.message_id, reply_markup=markup)
    elif call.data == "main_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🎮 قسم الألعاب", callback_data="games_menu"),
            types.InlineKeyboardButton("👨‍💻 الدعم الفني", callback_data="support_menu")
        )
        if chat_id == ADMIN_ID:
            markup.add(types.InlineKeyboardButton("📋 جميع الطلبات", callback_data="admin_view_orders"))
        bot.edit_message_text("🤖 اختر القسم المناسب من الأزرار أدناه:", chat_id, call.message.message_id, reply_markup=markup)
    elif call.data.startswith("buy_"):
        game_type = "ببجي موبايل" if "pubg" in call.data else "فري فاير"
        unit = "UC" if "pubg" in call.data else "جوهرة"
        amount = call.data.split("_")[-1]
        price_in_syr = round(PRICES.get(call.data, 0.0) * EXCHANGE_RATE)
        user_orders[call.from_user.id] = {"game": game_type, "amount": f"{amount} {unit}", "price_syr": price_in_syr, "step": "get_id"}
        bot.send_message(chat_id, f"🎮 الرجاء إدخال آيدي (ID) اللاعب الخاص بك لـ {game_type}:")
        bot.answer_callback_query(call.id)
    elif call.data == "admin_view_orders" and chat_id == ADMIN_ID:
        if os.path.exists(ORDERS_FILE) and os.path.getsize(ORDERS_FILE) > 0:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                orders_data = f.read()
            if len(orders_data) > 4000:
                with open(ORDERS_FILE, "rb") as f:
                    bot.send_document(chat_id, f, caption="📋 قائمة الطلبات الكاملة")
            else:
                bot.send_message(chat_id, f"📋 **الطلبات المسجلة:**\n\n{orders_data}")
        else:
            bot.send_message(chat_id, "📋 لا توجد طلبات مسجلة حتى الآن.")
        bot.answer_callback_query(call.id)
    elif call.data.startswith("accept_") or call.data.startswith("reject_"):
        if chat_id == ADMIN_ID:
            data_parts = call.data.split("_")
            action = str(data_parts[0])
            target_user_id = str(data_parts[1])
            if action == "accept":
                bot.send_message(target_user_id, "✅ **تمت العملية بنجاح!**\n\nلقد تم التحقق من عملية الدفع وشحن حسابك بالألعاب بنجاح.")
                bot.edit_message_text(f"{call.message.text}\n\n🟢 **حالة الطلب:** تم الشحن بنجاح ✅", chat_id, call.message.message_id)
            elif action == "reject":
                bot.send_message(target_user_id, "❌ **عذراً، تم رفض طلبك!**\n\nيرجى التأكد من رقم المعاملة أو التواصل مع الدعم.")
                bot.edit_message_text(f"{call.message.text}\n\n🔴 **حالة الطلب:** تم الرفض ❌", chat_id, call.message.message_id)
        bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.from_user.id in user_orders)
def process_order_steps(message):
    user_id = message.from_user.id
    step = user_orders[user_id]["step"]
    if step == "get_id":
        user_orders[user_id]["player_id"] = message.text
        user_orders[user_id]["step"] = "get_payment"
        bot.send_message(message.chat.id, f"💰 **خطوة الدفع:**\n\n💵 القيمة: **{user_orders[user_id]['price_syr']} ليرة سورية جديدة**\n📌 أرسل المبلغ لحساب الشام كاش: `{SHAM_CASH_ACCOUNT}`\n\n⚠️ بعد التحويل، اكتب رقم المعاملة هنا نصاً:")
    elif step == "get_payment":
        user_orders[user_id]["transaction_id"] = message.text
        order_info = user_orders[user_id]
        bot.send_message(message.chat.id, f"✅ **تم استلام طلبك بنجاح!**\n\n🎮 اللعبة: {order_info['game']}\n📦 الفئة: {order_info['amount']}\n🆔 الآيدي: `{order_info['player_id']}`\n\n⏳ جاري المراجعة والتحقق...")
        username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
        admin_notification = f"🚨 **طلب جديد!**\n\n👤 الزبون: {username} (ID: {user_id})\n🎮 اللعبة: {order_info['game']}\n📦 الكمية: {order_info['amount']}\n💰 المطلوب: {order_info['price_syr']} ل.س\n🆔 آيدي اللاعب: `{order_info['player_id']}`\n🧾 رقم المعاملة: `{order_info['transaction_id']}`"
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("🟢 شحن (صح)", callback_data=f"accept_{user_id}"),
            types.InlineKeyboardButton("🔴 رفض (خطأ)", callback_data=f"reject_{user_id}")
        )
        bot.send_message(ADMIN_ID, admin_notification, reply_markup=admin_markup)
        save_order_to_file(admin_notification)
        del user_orders[user_id]

if __name__ == "__main__":
    # تشغيل السيرفر المساعد لتفادي إغلاق Render المجاني
    keep_alive()
    bot.infinity_polling()
