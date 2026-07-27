import telebot
from telebot import types
import os
import requests
import uuid
from flask import Flask
from threading import Thread

# --- تشغيل سيرفر وهمي للحفاظ على مجانية Render ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Live and Running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- الإعدادات الأساسية للبوت ---
TOKEN = "8826744317:AAHR9wuT8sNK0Vg98uCcGmaps7-YntrSWiQ"
ADMIN_ID = 8192730669
SHAM_CASH_ACCOUNT = "df910e178e027a6bfcae8b9b06b5384"
EXCHANGE_RATE = 145

# --- إعدادات الـ API الخاصة بموقع نمر كارد ---
API_TOKEN = "AatfAkAcp6XKyQKPYru8ZyaAZ6H0VKyNb4FXx1sgbV8hAthEgw8Z0hQjNZNvcZs-"
BASE_URL = "https://nemer-card.com"

bot = telebot.TeleBot(TOKEN)
user_orders = {}
ORDERS_FILE = "all_orders.txt"

# تحديث الأسعار بدقة لتطابق فئات ببجي وفري فاير حسب الصور المرسلة
PRICES = {
    # ببجي موبايل 
    "buy_pubg_60": {"price_usd": 0.906, "api_id": 18},     # 🌟 استبدل بـ ID المنتج من نمر كارد
    "buy_pubg_325": {"price_usd": 4.558, "api_id": 325},   # 🌟 استبدل بـ ID المنتج من نمر كارد
    "buy_pubg_660": {"price_usd": 9.115, "api_id": 660},   # 🌟 استبدل بـ ID المنتج من نمر كارد
    "buy_pubg_1800": {"price_usd": 22.788, "api_id": 1800}, # 🌟 استبدل بـ ID المنتج من نمر كارد
    "buy_pubg_3850": {"price_usd": 45.320, "api_id": 3850}, # 🌟 استبدل بـ ID المنتج من نمر كارد
    "buy_pubg_8100": {"price_usd": 90.640, "api_id": 8100}, # 🌟 استبدل بـ ID المنتج من نمر كارد
    
    # فري فاير (محدثة بالكامل حسب الصورة الأخيرة)
    "buy_ff_110": {"price_usd": 0.951, "api_id": 110},     # 🌟 استبدل بـ ID المنتج من نمر كارد
    "buy_ff_200": {"price_usd": 1.912, "api_id": 200},     # 🌟 استبدل بـ ID المنتج من نمر كارد
    "buy_ff_530": {"price_usd": 4.783, "api_id": 530},     # 🌟 استبدل بـ ID المنتج من نمر كارد
    "buy_ff_1080": {"price_usd": 9.590, "api_id": 1080},   # 🌟 استبدل بـ ID المنتج من نمر كارد
    "buy_ff_2200": {"price_usd": 16.707, "api_id": 2200}   # 🌟 استبدل بـ ID المنتج من نمر كارد
}

def save_order_to_file(order_details):
    with open(ORDERS_FILE, "a", encoding="utf-8") as f:
        f.write(order_details + "\n" + "-"*30 + "\n")

# دالة إرسال الطلب تلقائياً إلى السيرفر المورد عبر الـ API
def send_order_to_api(product_id, player_id):
    url = f"{BASE_URL}/client/api/newOrder/{product_id}/params"
    headers = {
        "api-token": API_TOKEN,
        "Content-Type": "application/json"
    }
    order_uuid = str(uuid.uuid4())
    payload = {
        "qty": 1,
        "playerId": player_id,
        "order_uuid": order_uuid
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        return {"status": "ERROR", "message": f"Server error code {response.status_code}"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

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
            types.InlineKeyboardButton(f"📦 60 UC - {round(PRICES['buy_pubg_60']['price_usd'] * EXCHANGE_RATE)} ل.س", callback_data="buy_pubg_60"),
            types.InlineKeyboardButton(f"📦 325 UC - {round(PRICES['buy_pubg_325']['price_usd'] * EXCHANGE_RATE)} ل.س", callback_data="buy_pubg_325"),
            types.InlineKeyboardButton(f"📦 660 UC - {round(PRICES['buy_pubg_660']['price_usd'] * EXCHANGE_RATE)} ل.س", callback_data="buy_pubg_660"),
            types.InlineKeyboardButton(f"📦 1800 UC - {round(PRICES['buy_pubg_1800']['price_usd'] * EXCHANGE_RATE)} ل.س", callback_data="buy_pubg_1800"),
            types.InlineKeyboardButton(f"📦 3850 UC - {round(PRICES['buy_pubg_3850']['price_usd'] * EXCHANGE_RATE)} ل.س", callback_data="buy_pubg_3850"),
            types.InlineKeyboardButton(f"📦 8100 UC - {round(PRICES['buy_pubg_8100']['price_usd'] * EXCHANGE_RATE)} ل.س", callback_data="buy_pubg_8100"),
            types.InlineKeyboardButton("🔙 العودة", callback_data="games_menu")
        )
        bot.edit_message_text("📱 اختر الفئة المناسبة لببجي:", chat_id, call.message.message_id, reply_markup=markup)
    elif call.data == "ff_info":
        markup = types.InlineKeyboardMarkup(row_width=1)
        # تحديث الأزرار والمحاذاة الحسابية لفئات فري فاير الجديدة بالليرة السورية
        markup.add(
            types.InlineKeyboardButton(f"💎 110 Gems - {round(PRICES['buy_ff_110']['price_usd'] * EXCHANGE_RATE)} ل.س", callback_data="buy_ff_110"),
            types.InlineKeyboardButton(f"💎 200 Gems - {round(PRICES['buy_ff_200']['price_usd'] * EXCHANGE_RATE)} ل.س", callback_data="buy_ff_200"),
            types.InlineKeyboardButton(f"💎 530 Gems - {round(PRICES['buy_ff_530']['price_usd'] * EXCHANGE_RATE)} ل.س", callback_data="buy_ff_530"),
            types.InlineKeyboardButton(f"💎 1080 Gems - {round(PRICES['buy_ff_1080']['price_usd'] * EXCHANGE_RATE)} ل.س", callback_data="buy_ff_1080"),
            types.InlineKeyboardButton(f"💎 2200 Gems - {round(PRICES['buy_ff_2200']['price_usd'] * EXCHANGE_RATE)} ل.س", callback_data="buy_ff_2200"),
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
        item_config = PRICES.get(call.data)
        game_type = "ببجي موبايل" if "pubg" in call.data else "فري فاير"
        unit = "UC" if "pubg" in call.data else "جوهرة"
        amount = call.data.split("_")[-1]
        price_in_syr = round(item_config["price_usd"] * EXCHANGE_RATE)
        
        user_orders[call.from_user.id] = {
            "game": game_type, 
            "amount": f"{amount} {unit}", 
            "price_syr": price_in_syr, 
            "api_id": item_config["api_id"],
            "step": "get_id"
        }
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
                lines = call.message.text.split("\n")
                prod_id = None
                player_id = None
                
                for line in lines:
                    if "🆔" in line:
                        player_id = line.split("`")[1].strip()
                    if "🔢 معرف المنتج:" in line:
                        prod_id = line.split(":")[-1].strip()
                
                bot.send_message(ADMIN_ID, "⏳ جاري إرسال الطلب تلقائياً إلى سيرفر نمر كارد...")
                api_response = send_order_to_api(prod_id, player_id)
                
