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
    # تعديل جوهري: سحب المنفذ ديناميكياً من بيئة Render لتفادي الإغلاق المبكر
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

bot = telebot.TeleBot(TOKEN)
user_orders = {}
admin_steps = {} 
ORDERS_FILE = "all_orders.txt"

PRICES = {
    "buy_pubg_60": 0.92,
    "buy_pubg_325": 4.59,
    "buy_pubg_660": 9.19,
    "buy_ff_110": 0.98,
    "buy_ff_231": 1.96,
    "buy_card_google_5": 5.123,
    "buy_card_google_10": 10.246,
    "buy_card_google_25": 25.615,
    "buy_card_google_50": 51.23,
    "buy_card_apple_2": 1.976,
    "buy_card_apple_5": 4.966,
    "buy_card_apple_10": 9.932,
    "buy_card_apple_15": 14.323,
    "buy_card_apple_20": 19.604,
    "buy_card_apple_25": 23.942,
    "buy_card_apple_50": 49.009
}

def save_order_to_file(order_details):
    with open(ORDERS_FILE, "a", encoding="utf-8") as f:
        f.write(order_details + "\n" + "-"*30 + "\n")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_games = types.InlineKeyboardButton("🎮 قسم الألعاب", callback_data="games_menu")
    btn_cards = types.InlineKeyboardButton("💳 قسم البطاقات", callback_data="cards_menu")
    btn_support = types.InlineKeyboardButton("👨‍💻 الدعم الفني", callback_data="support_menu")
    markup.add(btn_games, btn_cards, btn_support)
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
        
    elif call.data == "cards_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🤖 غوغل امريكي", callback_data="google_cards"),
            types.InlineKeyboardButton("🍏 آيتونز / آبل", callback_data="apple_cards"),
            types.InlineKeyboardButton("🔙 العودة", callback_data="main_menu")
        )
        bot.edit_message_text("💳 اختر نوع البطاقات التي تريدها:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "google_cards":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"💳 غوغل 5$ - {round(PRICES['buy_card_google_5'] * EXCHANGE_RATE)} ل.س", callback_data="buy_card_google_5"),
            types.InlineKeyboardButton(f"💳 غوغل 10$ - {round(PRICES['buy_card_google_10'] * EXCHANGE_RATE)} ل.س", callback_data="buy_card_google_10"),
            types.InlineKeyboardButton(f"💳 غوغل 25$ - {round(PRICES['buy_card_google_25'] * EXCHANGE_RATE)} ل.س", callback_data="buy_card_google_25"),
            types.InlineKeyboardButton(f"💳 غوغل 50$ - {round(PRICES['buy_card_google_50'] * EXCHANGE_RATE)} ل.س", callback_data="buy_card_google_50"),
            types.InlineKeyboardButton("🔙 العودة", callback_data="cards_menu")
        )
        bot.edit_message_text("🤖 اختر فئة بطاقة غوغل بلاي الأمريكية:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "apple_cards":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(f"🍏 آيتونز 2$ - {round(PRICES['buy_card_apple_2'] * EXCHANGE_RATE)} ل.س", callback_data="buy_card_apple_2"),
            types.InlineKeyboardButton(f"🍏 آيتونز 5$ - {round(PRICES['buy_card_apple_5'] * EXCHANGE_RATE)} ل.س", callback_data="buy_card_apple_5"),
            types.InlineKeyboardButton(f"🍏 آيتونز 10$ - {round(PRICES['buy_card_apple_10'] * EXCHANGE_RATE)} ل.س", callback_data="buy_card_apple_10"),
            types.InlineKeyboardButton(f"🍏 آيتونز 15$ - {round(PRICES['buy_card_apple_15'] * EXCHANGE_RATE)} ل.س", callback_data="buy_card_apple_15"),
            types.InlineKeyboardButton(f"🍏 آيتونز 20$ - {round(PRICES['buy_card_apple_20'] * EXCHANGE_RATE)} ل.س", callback_data="buy_card_apple_20"),
            types.InlineKeyboardButton(f"🍏 آيتونز 25$ - {round(PRICES['buy_card_apple_25'] * EXCHANGE_RATE)} ل.س", callback_data="buy_card_apple_25"),
            types.InlineKeyboardButton(f"🍏 آيتونز 50$ - {round(PRICES['buy_card_apple_50'] * EXCHANGE_RATE)} ل.س", callback_data="buy_card_apple_50"),
            types.InlineKeyboardButton("❌ آيتونز 100$ (غير متاح)", callback_data="card_unavailable")
        )
        markup.add(types.InlineKeyboardButton("🔙 العودة", callback_data="cards_menu"))
        bot.edit_message_text("🍏 اختر فئة بطاقة آيتونز المتاحة:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "card_unavailable":
        bot.answer_callback_query(call.id, "⚠️ عذراً، هذه الفئة غير متوفرة حالياً!", show_alert=True)

    elif call.data == "pubg_info":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"📦 60 UC - {round(PRICES['buy_pubg_60'] * EXCHANGE_RATE)} ل.س", callback_data="buy_pubg_60"),
            types.InlineKeyboardButton(f"📦 325 UC - {round(PRICES['buy_pubg_325'] * EXCHANGE_RATE)} ل.س", callback_data="buy_pubg_325"),
            types.InlineKeyboardButton(f"📦 660 UC - {round(PRICES['buy_pubg_660'] * EXCHANGE_RATE)} ل.س", callback_data="buy_pubg_660"),
            types.InlineKeyboardButton("🔙 العودة", callback_data="games_menu")
        )
        bot.edit_message_text("📱 اختر الفئة المناسبة لببجي:", chat_id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "ff_info":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"💎 110 Gems - {round(PRICES['buy_ff_110'] * EXCHANGE_RATE)} ل.س", callback_data="buy_ff_110"),
            types.InlineKeyboardButton(f"💎 231 Gems - {round(PRICES['buy_ff_231'] * EXCHANGE_RATE)} ل.س", callback_data="buy_ff_231"),
            types.InlineKeyboardButton("🔙 العودة", callback_data="games_menu")
        )
        bot.edit_message_text("🔥 اختر الفئة المناسبة لفري فاير:", chat_id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "support_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("💬 تواصل مع الدعم", url="https://t.me"),
            types.InlineKeyboardButton("🔙 العودة", callback_data="main_menu")
        )
        bot.edit_message_text("👨‍💻 للدعم الفني تواصل معنا عبر الزر أدناه:", chat_id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "main_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🎮 قسم الألعاب", callback_data="games_menu"),
            types.InlineKeyboardButton("💳 قسم البطاقات", callback_data="cards_menu"),
            types.InlineKeyboardButton("👨‍💻 الدعم الفني", callback_data="support_menu")
        )
        if chat_id == ADMIN_ID:
            markup.add(types.InlineKeyboardButton("📋 جميع الطلبات", callback_data="admin_view_orders"))
        bot.edit_message_text("🤖 اختر القسم المناسب من الأزرار أدناه:", chat_id, call.message.message_id, reply_markup=markup)
        
    elif call.data.startswith("buy_"):
        if "card" in call.data:
            item_type = "بطاقة غوغل أمريكي" if "google" in call.data else "بطاقة آيتونز"
            unit = "دولار"
        else:
            item_type = "ببجي موبايل" if "pubg" in call.data else "فري فاير"
            unit = "UC" if "pubg" in call.data else "جوهرة"
            
        amount = call.data.split("_")[-1]
        price_in_syr = round(PRICES.get(call.data, 0.0) * EXCHANGE_RATE)
        
        user_orders[call.from_user.id] = {
            "game": item_type, 
            "amount": f"{amount} {unit}", 
            "price_syr": price_in_syr, 
            "step": "get_id"
        }
        
        msg_text = f"📧 الرجاء إدخال البريد الإلكتروني أو رقم الواتساب المراد استلام كود الـ {item_type} عليه:" if "card" in call.data else f"🎮 الرجاء إدخال آيدي (ID) اللاعب الخاص بك لـ {item_type}:"
        bot.send_message(chat_id, msg_text)
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
