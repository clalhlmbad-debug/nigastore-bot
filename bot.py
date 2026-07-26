import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# تفعيل سيرفر وهمي للحفاظ على مجانية Render
app = Flask('')

@app.route('/')
def home():
    return "Bot is Live and Running!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- الإعدادات الأساسية للبوت ---
TOKEN = "8020744317:AAHmTmreEVhina7QpODQQOq7-tKGH54yPXK"
ADMIN_ID = 8192730609
SHAM_CASH_ACCOUNT = "df018e178a027a6fbca89b9b6b5384"
EXCHANGE_RATE = 145

bot = telebot.TeleBot(TOKEN)
user_orders = {}
admin_actions = {}  # لتتبع حالة انتظار كود البطاقة من الأدمن
ORDERS_FILE = "all_orders.txt"

PRICES = {
    "buy_pubg_60": 0.92,
    "buy_pubg_325": 4.59,
    "buy_ff_660": 9.19,
    "buy_ff_110": 0.98,
    "buy_ff_231": 1.96,
    
    # فئات بطاقات آيتونز
    "buy_itunes_2": 1.976,
    "buy_itunes_5": 4.966,
    "buy_itunes_10": 9.932,
    "buy_itunes_15": 14.323,
    "buy_itunes_20": 19.604,
    "buy_itunes_25": 23.942,
    "buy_itunes_50": 49.009,
    "buy_itunes_100": 95.663,
    
    # فئات بطاقات غوغل بلاي الأمريكي
    "buy_google_5": 5.123,
    "buy_google_10": 10.246,
    "buy_google_25": 25.615,
    "buy_google_50": 51.23
}

def save_order_to_file(order_details):
    with open(ORDERS_FILE, "a", encoding="utf-8") as f:
        f.write(order_details + "\n" + "-"*30 + "\n")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_games = types.InlineKeyboardButton("🎮 قسم الألعاب والبطاقات", callback_data="games_menu")
    btn_support = types.InlineKeyboardButton("💬 الدعم الفني", url="https://t.me")
    markup.add(btn_games, btn_support)
    
    if message.chat.id == ADMIN_ID:
        btn_admin = types.InlineKeyboardButton("📜 جميع الطلبات", callback_data="admin_view_orders")
        markup.add(btn_admin)
        
    welcome_text = f"👋 أهلاً بك في Niga Store! اختر من القائمة أدناه:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    if call.data == "games_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🔫 ببجي موبايل", callback_data="pubg_info"),
            types.InlineKeyboardButton("🔥 فري فاير", callback_data="ff_info"),
            types.InlineKeyboardButton("💳 البطاقات الرقمية", callback_data="cards_menu")
        )
        markup.add(types.InlineKeyboardButton("🔙 العودة", callback_data="main_menu"))
        bot.edit_message_text("👇 اختر القسم المناسب:", chat_id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "pubg_info":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"🎁 60 UC - {round(0.92 * EXCHANGE_RATE)} ل.س", callback_data="buy_pubg_60"),
            types.InlineKeyboardButton(f"🎁 325 UC - {round(4.59 * EXCHANGE_RATE)} ل.س", callback_data="buy_pubg_325"),
            types.InlineKeyboardButton("🔙 العودة", callback_data="games_menu")
        )
        bot.edit_message_text("🛒 اختر الفئة المناسبة لببجي:", chat_id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "ff_info":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"💎 110 Gems - {round(0.98 * EXCHANGE_RATE)} ل.س", callback_data="buy_ff_110"),
            types.InlineKeyboardButton(f"💎 231 Gems - {round(1.96 * EXCHANGE_RATE)} ل.س", callback_data="buy_ff_231"),
            types.InlineKeyboardButton(f"💎 660 Gems - {round(9.19 * EXCHANGE_RATE)} ل.س", callback_data="buy_ff_660"),
            types.InlineKeyboardButton("🔙 العودة", callback_data="games_menu")
        )
        bot.edit_message_text("🛒 اختر الفئة المناسبة لفري فاير:", chat_id, call.message.message_id, reply_markup=markup)

    # قائمة اختيار نوع البطاقات الرقمية
    elif call.data == "cards_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🍏 بطاقات iTunes", callback_data="itunes_menu"),
            types.InlineKeyboardButton("🤖 بطاقات Google Play", callback_data="google_menu")
        )
        markup.add(types.InlineKeyboardButton("🔙 العودة للقائمة السابقة", callback_data="games_menu"))
        bot.edit_message_text("💳 اختر نوع البطاقات الرقمية التي تريد تصفحها:", chat_id, call.message.message_id, reply_markup=markup)

    # قائمة فئات iTunes
    elif call.data == "itunes_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(f"🍏 iTunes 2$ - {round(1.976 * EXCHANGE_RATE)} ل.س", callback_data="buy_itunes_2"),
            types.InlineKeyboardButton(f"🍏 iTunes 5$ - {round(4.966 * EXCHANGE_RATE)} ل.س", callback_data="buy_itunes_5"),
            types.InlineKeyboardButton(f"🍏 iTunes 10$ - {round(9.932 * EXCHANGE_RATE)} ل.س", callback_data="buy_itunes_10"),
            types.InlineKeyboardButton(f"🍏 iTunes 15$ - {round(14.323 * EXCHANGE_RATE)} ل.س", callback_data="buy_itunes_15"),
            types.InlineKeyboardButton(f"🍏 iTunes 20$ - {round(19.604 * EXCHANGE_RATE)} ل.س", callback_data="buy_itunes_20"),
            types.InlineKeyboardButton(f"🍏 iTunes 25$ - {round(23.942 * EXCHANGE_RATE)} ل.س", callback_data="buy_itunes_25"),
            types.InlineKeyboardButton(f"🍏 iTunes 50$ - {round(49.009 * EXCHANGE_RATE)} ل.س", callback_data="buy_itunes_50"),
            types.InlineKeyboardButton(f"🍏 iTunes 100$ - {round(95.663 * EXCHANGE_RATE)} ل.س", callback_data="buy_itunes_100")
        )
        markup.add(types.InlineKeyboardButton("🔙 العودة", callback_data="cards_menu"))
        bot.edit_message_text("🍏 اختر فئة بطاقة iTunes المطلوبة:", chat_id, call.message.message_id, reply_markup=markup)

    # قائمة فئات Google Play
    elif call.data == "google_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(f"🤖 Google 5$ - {round(5.123 * EXCHANGE_RATE)} ل.س", callback_data="buy_google_5"),
            types.InlineKeyboardButton(f"🤖 Google 10$ - {round(10.246 * EXCHANGE_RATE)} ل.س", callback_data="buy_google_10"),
            types.InlineKeyboardButton(f"🤖 Google 25$ - {round(25.615 * EXCHANGE_RATE)} ل.س", callback_data="buy_google_25"),
            types.InlineKeyboardButton(f"🤖 Google 50$ - {round(51.23 * EXCHANGE_RATE)} ل.س", callback_data="buy_google_50")
        )
        markup.add(types.InlineKeyboardButton("🔙 العودة", callback_data="cards_menu"))
        bot.edit_message_text("🤖 اختر فئة بطاقة Google Play الأمريكي المطلوبة:", chat_id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "main_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🎮 قسم الألعاب والبطاقات", callback_data="games_menu"),
            types.InlineKeyboardButton("💬 الدعم الفني", url="https://t.me")
        )
        if chat_id == ADMIN_ID:
            markup.add(types.InlineKeyboardButton("📜 جميع الطلبات", callback_data="admin_view_orders"))
        bot.edit_message_text("👋 أهلاً بك في Niga Store! اختر من القائمة أدناه:", chat_id, call.message.message_id, reply_markup=markup)
        
    if chat_id == ADMIN_ID and call.data == "admin_view_orders":
        if os.path.exists(ORDERS_FILE) and os.path.getsize(ORDERS_FILE) > 0:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                orders_data = f.read()
            if len(orders_data) > 4000:
                with open(ORDERS_FILE, "rb") as f:
                    bot.send_document(chat_id, f, caption="📜 الملف الكامل لكافة الطلبات")
            else:
                bot.send_message(chat_id, f"📜 الطلبات المسجلة حتى الآن:\n\n{orders_data}")
        else:
            bot.send_message(chat_id, "❌ لا توجد طلبات مسجلة حتى الآن.")
        bot.answer_callback_query(call.id)

    if call.data.startswith("buy_"):
        if "pubg" in call.data:
            game_type, unit = "ببجي موبايل", "UC"
            amount = call.data.split("_")[-1]
        elif "ff" in call.data:
            game_type, unit = "فري فاير", "جوهرة"
            amount = call.data.split("_")[-1]
        elif "itunes" in call.data:
            game_type, unit = "بطاقات iTunes", "دولار آيتونز"
            amount = call.data.split("_")[-1]
        elif "google" in call.data:
            game_type, unit = "بطاقات Google Play", "دولار غوغل"
            amount = call.data.split("_")[-1]
        
        price_in_syr = round(PRICES[call.data] * EXCHANGE_RATE)
        user_orders[call.from_user.id] = {"game": game_type, "amount": f"{amount} {unit}", "price": price_in_syr, "item_key": call.data}
        
        bot.send_message(chat_id, f"🛒 لقد اخترت شحن {amount} {unit} من قسم {game_type}.\n\n💵 التكلفة: {price_in_syr} ل.س.\n\n🆔 الرجاء إرسال الـ ID الخاص بك أو الحساب المراد الشحن له الآن لإتمام العملية:")
        bot.answer_callback_query(call.id)

    if call.data.startswith("accept_") or call.data.startswith("reject_"):
        if chat_id == ADMIN_ID:
            data_parts = call.data.split("_")
            action = data_parts[0]
            target_user_id = int(data_parts[1])
            item_type = data_parts[2] if len(data_parts) > 2 else "game"
            
            if action == "accept":
                if item_type in ["itunes", "google"]:
                    admin_actions[ADMIN_ID] = {"action": "waiting_for_code", "target_user": target_user_id, "message_id": call.message.message_id}
                    bot.send_message(ADMIN_ID, f"📝 هذا الطلب تابع لقسم البطاقات الرقمية ({item_type}).\nالرجاء كتابة كود البطاقة الآن لإرساله تلقائياً للعميل:")
                else:
                    try:
