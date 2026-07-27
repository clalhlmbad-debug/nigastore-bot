import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# Render لتشغيل سيرفر وهمي للحفاظ على مجانية الـ
app = Flask('')

@app.route('/')
def home():
    return "Bot is Live and Running!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ---- الإعدادات الأساسية للبوت ----
TOKEN = "8826744317:AAHR9wuT8sNK0Vg98uCcGmaps7-YntrSWiQ"
ADMIN_ID = 8102730609
SHAM_CASH_ACCOUNT = "df101ae178a027fa6fbca89b9b6b5384"
EXCHANGE_RATE = 145

bot = telebot.TeleBot(TOKEN)
user_orders = {}
admin_actions = {}  # لتتبع حالة انتظار كود البطاقة من الأدمن
ORDERS_FILE = "all_orders.txt"

# PRICES
PRICES = {
    "buy_pubg_60": 0.92,
    "buy_pubg_325": 4.59,
    "buy_ff_660": 0.19,
    "buy_ff_110": 0.98,
    "buy_ff_231": 1.96,
    
    # فئات شدات البوتزار #
    "buy_itunes_2": 1.976,
    "buy_itunes_5": 4.966,
    "buy_itunes_10": 9.932,
    "buy_itunes_15": 14.323,
    "buy_itunes_20": 19.604,
    "buy_itunes_25": 23.942,
    "buy_itunes_50": 49.009,
    "buy_itunes_100": 95.663,
    
    # فئات بطاقات جوجل بلاي الأمريكي #
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
    btn_games = types.InlineKeyboardButton("قسم الالعاب والبطاقات", callback_data="games_menu")
    btn_support = types.InlineKeyboardButton("الدعم الفني", url="https://t.me")
    markup.add(btn_games, btn_support)
    
    if message.chat.id == ADMIN_ID:
        btn_admin = types.InlineKeyboardButton("جميع الطلبات", callback_data="admin_view_orders")
        markup.add(btn_admin)
        
    welcome_text = f"مرحباً بك في Niga store أقدم لك:\nاختر من القائمة أدناه لشراء المنتجات."
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    if call.data == "games_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        # قائمة اختيار نوع البطاقات الرقمية #
        markup.add(
            types.InlineKeyboardButton("ببجي موبايل", callback_data="pubg_info"),
            types.InlineKeyboardButton("فري فاير", callback_data="ff_info"),
            types.InlineKeyboardButton("بطاقات رقمية", callback_data="cards_menu")
        )
        markup.add(types.InlineKeyboardButton("العودة للقائمة السابقة", callback_data="main_menu"))
        bot.edit_message_text(f"اختر القسم المناسب لك:", chat_id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "pubg_info":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"60 UC - {round(0.92 * EXCHANGE_RATE)} ل.س", callback_data="buy_pubg_60"),
            types.InlineKeyboardButton(f"325 UC - {round(4.59 * EXCHANGE_RATE)} ل.س", callback_data="buy_pubg_325")
        )
        markup.add(types.InlineKeyboardButton("العودة", callback_data="games_menu"))
        bot.edit_message_text("اختر الفئة المناسبة لببجي:", chat_id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "ff_info":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"110 Gems - {round(0.98 * EXCHANGE_RATE)} ل.س", callback_data="buy_ff_110"),
            types.InlineKeyboardButton(f"231 Gems - {round(1.96 * EXCHANGE_RATE)} ل.س", callback_data="buy_ff_231"),
            types.InlineKeyboardButton(f"660 Gems - {round(0.19 * EXCHANGE_RATE)} ل.س", callback_data="buy_ff_660")
        )
        markup.add(types.InlineKeyboardButton("العودة", callback_data="games_menu"))
        bot.edit_message_text("اختر الفئة المناسبة لفرى فاير:", chat_id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "cards_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("بطاقات iTunes", callback_data="itunes_menu"),
            types.InlineKeyboardButton("بطاقات Google play", callback_data="google_menu")
        )
        markup.add(types.InlineKeyboardButton("العودة للقائمة السابقة", callback_data="games_menu"))
        bot.edit_message_text("اختر نوع البطاقات الرقمية التي تريد تصفحها:", chat_id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "itunes_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(f"iTunes 2$ - {round(1.976 * EXCHANGE_RATE)} ل.س", callback_data="buy_itunes_2"),
            types.InlineKeyboardButton(f"iTunes 5$ - {round(4.966 * EXCHANGE_RATE)} ل.س", callback_data="buy_itunes_5"),
            types.InlineKeyboardButton(f"iTunes 10$ - {round(9.932 * EXCHANGE_RATE)} ل.س", callback_data="buy_itunes_10"),
            types.InlineKeyboardButton(f"iTunes 15$ - {round(14.323 * EXCHANGE_RATE)} ل.س", callback_data="buy_itunes_15"),
            types.InlineKeyboardButton(f"iTunes 20$ - {round(19.604 * EXCHANGE_RATE)} ل.س", callback_data="buy_itunes_20"),
            types.InlineKeyboardButton(f"iTunes 25$ - {round(23.942 * EXCHANGE_RATE)} ل.س", callback_data="buy_itunes_25"),
            types.InlineKeyboardButton(f"iTunes 50$ - {round(49.009 * EXCHANGE_RATE)} ل.س", callback_data="buy_itunes_50"),
            types.InlineKeyboardButton(f"iTunes 100$ - {round(95.663 * EXCHANGE_RATE)} ل.س", callback_data="buy_itunes_100")
        )
        markup.add(types.InlineKeyboardButton("العودة", callback_data="cards_menu"))
        bot.edit_message_text("بطاقات iTunes المطلوبة اختر فئة بطاقتك:", chat_id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "google_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(f"Google 5$ - {round(5.123 * EXCHANGE_RATE)} ل.س", callback_data="buy_google_5"),
            types.InlineKeyboardButton(f"Google 10$ - {round(10.246 * EXCHANGE_RATE)} ل.س", callback_data="buy_google_10"),
            types.InlineKeyboardButton(f"Google 25$ - {round(25.615 * EXCHANGE_RATE)} ل.س", callback_data="buy_google_25"),
            types.InlineKeyboardButton(f"Google 50$ - {round(51.23 * EXCHANGE_RATE)} ل.س", callback_data="buy_google_50")
        )
        markup.add(types.InlineKeyboardButton("العودة", callback_data="cards_menu"))
        bot.edit_message_text("بطاقات Google Play الأمريكي المطلوبة اختر فئة بطاقتك:", chat_id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "main_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_games = types.InlineKeyboardButton("قسم الالعاب والبطاقات", callback_data="games_menu")
        btn_support = types.InlineKeyboardButton("الدعم الفني", url="https://t.me")
        markup.add(btn_games, btn_support)
        
        if chat_id == ADMIN_ID:
            btn_admin = types.InlineKeyboardButton("جميع الطلبات", callback_data="admin_view_orders")
            markup.add(btn_admin)
            
        bot.edit_message_text("مرحباً بك في Niga store أقدم لك:", chat_id, call.message.message_id, reply_markup=markup)
        
    if chat_id == ADMIN_ID and call.data == "admin_view_orders":
        if os.path.exists(ORDERS_FILE) and os.path.getsize(ORDERS_FILE) > 0:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                orders_data = f.read()
            if len(orders_data) > 4000:
                with open(ORDERS_FILE, "rb") as f:
                    bot.send_document(chat_id, f, caption="الملفات والطلبات")
            else:
                bot.send_message(chat_id, f"الطلبات المسجلة حتى الآن:\n\n{orders_data}")
        else:
            bot.send_message(chat_id, "لا توجد طلبات مسجلة حتى الآن ❌")
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
            game_type, unit = "بطاقات Google Play", "دولار جوجل"
            amount = call.data.split("_")[-1]
            
        price_in_syr = round(PRICES[call.data] * EXCHANGE_RATE)
        user_orders[call.message.from_user.id] = {"game": game_type, "type": unit, "amount": amount, "price": price_in_syr}
        
        bot.send_message(chat_id, f"سعر المنتج هو {price_in_syr} ل.س ...")
        bot.answer_callback_query(call.id)
        
    if call.data.startswith("accept_") or call.data.startswith("reject_"):
        if chat_id == ADMIN_ID:
            data_parts = call.data.split("_")
            action = data_parts
            target_user_id = int(data_parts)
            item_type = data_parts if len(data_parts) > 2 else "game"
            
            if action == "accept":
                if item_type in ["itunes", "google"]:
                    admin_actions[ADMIN_ID] = {"action": "waiting_for_code", "user_id": target_user_id}
                    bot.send_message(ADMIN_ID, "الرجاء أرسل كود البطاقة للعميل:")
                else:
                    pass

# تشغيل السيرفر الوهمي لحماية البوت من التوقف
keep_alive()

# تشغيل استقبال الرسائل المستمر للبوت داخل تيليجرام
bot.infinity_polling(timeout=10, long_polling_timeout=5)
