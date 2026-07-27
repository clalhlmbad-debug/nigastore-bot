import telebot
from telebot import types
import os
import uuid
from flask import Flask
from threading import Thread

# --- إعدادات البوت والمسؤول ---
TOKEN = "8826744317:AAHR9wuT8sNK0Vg98uCcGmaps7-YntrSWiQ"
ADMIN_ID = 8192730669
EXCHANGE_RATE = 145  

PAYMENT_METHODS = {
    "sham_cash": {"name": "💳 شام كاش", "account": "df910e178e027a6bfcae8b9b06b5384"},
    "syriatel_cash": {"name": "📱 سيريتل كاش (تحويل يدوي حصراً)", "account": "0998211716"}
}

bot = telebot.TeleBot(TOKEN)
user_orders = {}  
admin_steps = {}  
ORDERS_FILE = "all_orders.txt"

PRICES = {
    "pubg_60": {"name": "ببجي 60 UC", "usd": 0.906, "input": "🆔 آيدي اللاعب:"},
    "pubg_325": {"name": "ببجي 325 UC", "usd": 4.558, "input": "🆔 آيدي اللاعب:"},
    "pubg_660": {"name": "ببجي 660 UC", "usd": 9.115, "input": "🆔 آيدي اللاعب:"},
    "ff_110": {"name": "فري فاير 110 جوهرة", "usd": 0.951, "input": "🆔 آيدي اللاعب:"},
    "ff_530": {"name": "فري فاير 530 جوهرة", "usd": 4.783, "input": "🆔 آيدي اللاعب:"},
    "google_5": {"name": "بطاقة غوغل 5$", "usd": 5.123, "input": "📧 البريد الإلكتروني أو الواتساب:"},
    "google_10": {"name": "بطاقة غوغل 10$", "usd": 10.246, "input": "📧 البريد الإلكتروني أو الواتساب:"},
    "apple_5": {"name": "بطاقة آيتونز 5$", "usd": 4.966, "input": "📧 البريد الإلكتروني أو الواتساب:"},
    "apple_10": {"name": "بطاقة آيتونز 10$", "usd": 9.932, "input": "📧 البريد الإلكتروني أو الواتساب:"},
    "tg_premium_1m": {"name": "تليجرام مميز (شهر)", "usd": 3.99, "input": "👤 معرف حسابك (@username):"},
    "tg_premium_3m": {"name": "تليجرام مميز (3 أشهر)", "usd": 11.99, "input": "👤 معرف حسابك (@username):"},
    "netflix_1m": {"name": "حساب نتفلكس (شهر)", "usd": 4.50, "input": "📧 إيميل استلام الحساب:"},
    "insta_1k": {"name": "1000 متابع إنستغرام", "usd": 1.20, "input": "🔗 رابط الحساب أو المقطع:"},
    "tiktok_1k": {"name": "1000 متابع تيك توك", "usd": 1.50, "input": "🔗 رابط الحساب أو المقطع:"}
}

def save_order_to_file(order_details):
    with open(ORDERS_FILE, "a", encoding="utf-8") as f:
        f.write(order_details + "\n" + "-"*30 + "\n")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎮 قسم الألعاب", callback_data="cat_games"),
        types.InlineKeyboardButton("💳 قسم البطاقات", callback_data="cat_cards"),
        types.InlineKeyboardButton("📱 شحن البرامج", callback_data="cat_apps"),
        types.InlineKeyboardButton("🚀 السوشيال ميديا", callback_data="cat_social"),
        types.InlineKeyboardButton("👨‍💻 الدعم الفني", callback_data="support_menu")
    )
    if message.chat.id == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("📋 سجل الأرشيف كاملاً", callback_data="admin_view_orders"))
    welcome_text = f"👋 مرحباً بك في متجر **Niga Store** المتكامل!\n\n📌 سعر الصرف المعتمد: 1$ = {EXCHANGE_RATE} ل.س\n\n⚡ اختر القسم الذي ترغب بتصفحه من الأزرار أدناه:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "main_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🎮 قسم الألعاب", callback_data="cat_games"),
            types.InlineKeyboardButton("💳 قسم البطاقات", callback_data="cat_cards"),
            types.InlineKeyboardButton("📱 شحن البرامج", callback_data="cat_apps"),
            types.InlineKeyboardButton("🚀 السوشيال ميديا", callback_data="cat_social"),
            types.InlineKeyboardButton("👨‍💻 الدعم الفني", callback_data="support_menu")
        )
        if chat_id == ADMIN_ID:
            markup.add(types.InlineKeyboardButton("📋 سجل الأرشيف كاملاً", callback_data="admin_view_orders"))
        bot.edit_message_text("🤖 اختر القسم المناسب من الأزرار أدناه:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "cat_games":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"📦 {PRICES['pubg_60']['name']} - {round(PRICES['pubg_60']['usd']*EXCHANGE_RATE)} ل.س", callback_data="prod_pubg_60"),
            types.InlineKeyboardButton(f"📦 {PRICES['pubg_325']['name']} - {round(PRICES['pubg_325']['usd']*EXCHANGE_RATE)} ل.س", callback_data="prod_pubg_325"),
            types.InlineKeyboardButton(f"📦 {PRICES['pubg_660']['name']} - {round(PRICES['pubg_660']['usd']*EXCHANGE_RATE)} ل.س", callback_data="prod_pubg_660"),
            types.InlineKeyboardButton(f"💎 {PRICES['ff_110']['name']} - {round(PRICES['ff_110']['usd']*EXCHANGE_RATE)} ل.س", callback_data="prod_ff_110"),
            types.InlineKeyboardButton(f"💎 {PRICES['ff_530']['name']} - {round(PRICES['ff_530']['usd']*EXCHANGE_RATE)} ل.س", callback_data="prod_ff_530"),
            types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")
        )
        bot.edit_message_text("🎮 اختر الفئة المناسبة لشحن لعبتك:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "cat_cards":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"🤖 {PRICES['google_5']['name']} - {round(PRICES['google_5']['usd']*EXCHANGE_RATE)} ل.س", callback_data="prod_google_5"),
            types.InlineKeyboardButton(f"🤖 {PRICES['google_10']['name']} - {round(PRICES['google_10']['usd']*EXCHANGE_RATE)} ل.س", callback_data="prod_google_10"),
            types.InlineKeyboardButton(f"🍏 {PRICES['apple_5']['name']} - {round(PRICES['apple_5']['usd']*EXCHANGE_RATE)} ل.س", callback_data="prod_apple_5"),
            types.InlineKeyboardButton(f"🍏 {PRICES['apple_10']['name']} - {round(PRICES['apple_10']['usd']*EXCHANGE_RATE)} ل.س", callback_data="prod_apple_10"),
            types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")
        )
        bot.edit_message_text("💳 اختر بطاقة الشحن المطلوبة:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "cat_apps":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"⭐ {PRICES['tg_premium_1m']['name']} - {round(PRICES['tg_premium_1m']['usd']*EXCHANGE_RATE)} ل.س", callback_data="prod_tg_premium_1m"),
            types.InlineKeyboardButton(f"⭐ {PRICES['tg_premium_3m']['name']} - {round(PRICES['tg_premium_3m']['usd']*EXCHANGE_RATE)} ل.س", callback_data="prod_tg_premium_3m"),
            types.InlineKeyboardButton(f"🎬 {PRICES['netflix_1m']['name']} - {round(PRICES['netflix_1m']['usd']*EXCHANGE_RATE)} ل.س", callback_data="prod_netflix_1m"),
            types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")
        )
        bot.edit_message_text("📱 اختر اشتراك التطبيق المطلوب:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "cat_social":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"📸 {PRICES['insta_1k']['name']} - {round(PRICES['insta_1k']['usd']*EXCHANGE_RATE)} ل.س", callback_data="prod_insta_1k"),
            types.InlineKeyboardButton(f"🎵 {PRICES['tiktok_1k']['name']} - {round(PRICES['tiktok_1k']['usd']*EXCHANGE_RATE)} ل.س", callback_data="prod_tiktok_1k"),
            types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")
        )
        bot.edit_message_text("🚀 اختر خدمة دعم السوشيال ميديا:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "support_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("💬 تواصل مباشرة عبر المطور", url="https://t.me"),
            types.InlineKeyboardButton("🔙 العودة", callback_data="main_menu")
        )
        bot.edit_message_text("👨‍💻 للدعم الفني، الاستفسارات الشاملة أو حل المشاكل، انقر فوق الزر أدناه للتواصل معنا:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("prod_"):
        prod_key = call.data.replace("prod_", "")
        item_data = PRICES.get(prod_key)
        price_syr = round(item_data["usd"] * EXCHANGE_RATE)
        
        user_orders[call.from_user.id] = {
            "item_name": item_data["name"],
            "price_syr": price_syr,
            "step": "get_target_id",
            "input_label": item_data["input"]
        }
        bot.send_message(chat_id, f"📝 لقد اخترت: **{item_data['name']}**\n\n✍️ {item_data['input']}", parse_mode="Markdown")
        bot.answer_callback_query(call.id)

    elif call.data.startswith("pay_"):
        parts = call.data.split("_")
        method_key = "_".join(parts[1:-1])
        u_id = int(parts[-1])
        
        if u_id in user_orders and user_orders[u_id]["step"] == "select_payment":
            method_info = PAYMENT_METHODS.get(method_key)
            user_orders[u_id]["payment_method"] = method_info["name"]
            user_orders[u_id]["step"] = "get_transaction"
            
            additional_note = "\n⚠️ **ملاحظة هامة:** يرجى الانتباه أن التحويل عبر سيريتل كاش يجب أن يكون يدويّاً حصراً من خطك!" if method_key == "syriatel_cash" else ""
            
            pay_instruction = f"💸 **⚡ تعليمات التحويل عبر {method_info['name']}:**\n\n📌 يرجى إرسال مبلغ قدره: **{user_orders[u_id]['price_syr']} ل.س**\n📥 إلى الحساب أو الرقم التالي: `{method_info['account']}`{additional_note}\n\n⚠️ **بعد إتمام التحويل الناجح:**\nاكتب هنا في الشات رقم المعاملة أو الإشعار نصاً لتأكيد طلبك:"
            bot.send_message(chat_id, pay_instruction, parse_mode="Markdown")
            bot.answer_callback_query(call.id)

    elif call.data == "admin_view_orders" and chat_id == ADMIN_ID:
        if os.path.exists(ORDERS_FILE) and os.path.getsize(ORDERS_FILE) > 0:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
