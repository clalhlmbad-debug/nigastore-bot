import os
import uuid
import telebot
from telebot import types
from flask import Flask
from threading import Thread
import requests

# ==========================================
# 1. الإعدادات الأساسية (تأكد من توكن BotFather الجديد)
# ==========================================
TOKEN = "8826744317:AAFho5aCppPS1we_4kkp4Rz1SX6fh32K-Y8" 
ADMIN_ID = 8192730669
SHAM_CASH_ACCOUNT = "df910e11786027a6bfcae8b9b06b5384"
EXCHANGE_RATE = 145

NEMER_API_TOKEN = "ضع_api_token_الخاص_بك_من_نمر_كارد"
BASE_URL = "https://nemer-card.com"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# ==========================================
# 2. قواعد البيانات الافتراضية لحفظ الحسابات مجاناً
# ==========================================
# ملاحظة: لحفظ البيانات بشكل دائم عند إعادة تشغيل سيرفر رندر المجاني يفضل ربطها بـ MongoDB لاحقاً
user_wallets = {}  # لحفظ رصيد المستخدمين {chat_id: balance_syp}
user_history = {}  # لحفظ أرشيف الطلبات {chat_id: [قائمة الطلبات]}
all_users = set()  # لحفظ الـ IDs لجميع من ضغط start للإذاعة الجماعية

PRICES = {
    # باقات ببجي موبايل
    "pubg_60": {"name": "60 UC", "price_usd": 0.92, "nemer_id": 365},
    "pubg_325": {"name": "325 UC", "price_usd": 4.59, "nemer_id": 18},
    "pubg_660": {"name": "660 UC", "price_usd": 9.19, "nemer_id": 103},
    "pubg_1800": {"name": "1800 UC", "price_usd": 22.97, "nemer_id": 104},
    "pubg_3850": {"name": "3850 UC", "price_usd": 45.94, "nemer_id": 105},
    "pubg_8100": {"name": "8100 UC", "price_usd": 91.88, "nemer_id": 106},
    
    # فئات بطاقات آيتونز
    "itunes_2usd": {"name": "Itunes 2$ US GiftCard", "price_usd": 1.98, "nemer_id": 301},
    "itunes_3usd": {"name": "Itunes 3$ US GiftCard", "price_usd": 2.98, "nemer_id": 302},
    "itunes_4usd": {"name": "Itunes 4$ US GiftCard", "price_usd": 3.97, "nemer_id": 303},
    "itunes_5usd": {"name": "Itunes 5$ US GiftCard", "price_usd": 4.96, "nemer_id": 304},
    "itunes_6usd": {"name": "Itunes 6$ US GiftCard", "price_usd": 5.95, "nemer_id": 305},
    "itunes_7usd": {"name": "Itunes 7$ US GiftCard", "price_usd": 6.95, "nemer_id": 306},
    "itunes_8usd": {"name": "Itunes 8$ US GiftCard", "price_usd": 7.94, "nemer_id": 307},
    "itunes_9usd": {"name": "Itunes 9$ US GiftCard", "price_usd": 8.93, "nemer_id": 308},
    "itunes_10usd": {"name": "Itunes 10$ US GiftCard", "price_usd": 9.92, "nemer_id": 309},
    "itunes_15usd": {"name": "Itunes 15$ US GiftCard", "price_usd": 14.88, "nemer_id": 310},
    "itunes_20usd": {"name": "Itunes 20$ US GiftCard", "price_usd": 19.84, "nemer_id": 311},
    "itunes_25usd": {"name": "Itunes 25$ US GiftCard", "price_usd": 24.81, "nemer_id": 312}
}

user_orders = {}

@app.route('/')
def home():
    return "Bot is Live and Running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# 3. القائمة الرئيسية (لوحة الكيبورد السفلي)
# ==========================================
@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    all_users.add(chat_id)
    
    # تهيئة المحفظة والأرشيف للمستخدم الجديد إن لم يكن مسجلاً
    if chat_id not in user_wallets:
        user_wallets[chat_id] = 0.0
    if chat_id not in user_history:
        user_history[chat_id] = []
        
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn_pubg = types.KeyboardButton("PUBG MOBILE ⚡")
    btn_ff = types.KeyboardButton("FREE FIRE 🔥")
    btn_codes = types.KeyboardButton("أكواد وبطاقات")
    btn_other = types.KeyboardButton("شحن رصيد المحفظة 💰")
    btn_manual = types.KeyboardButton("المنتجات اليدوية 🛍️")
    btn_my_account = types.KeyboardButton("حسابي 👤")
    btn_my_orders = types.KeyboardButton("طلباتي 📂")
    btn_support = types.KeyboardButton("الدعم 📞")
    btn_info = types.KeyboardButton("تعليمات هامة ℹ️")
    
    markup.add(btn_pubg, btn_ff)
    markup.add(btn_codes, btn_other)
    markup.add(btn_manual, btn_my_account)
    markup.add(btn_my_orders)
    markup.add(btn_support, btn_info)
    
    bot.send_message(message.chat.id, "⬇️ مرحباً بك في متجرنا المتكامل والذكي ⬇️", reply_markup=markup)

# ==========================================
# 4. معالجة القوائم الفرعية للألعاب والبطاقات
# ==========================================
@bot.message_handler(func=lambda message: message.text == "PUBG MOBILE ⚡")
def show_pubg_packages(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for key in ["pubg_60", "pubg_325", "pubg_660", "pubg_1800", "pubg_3850", "pubg_8100"]:
        markup.add(types.InlineKeyboardButton(f"{PRICES[key]['name']} - ${PRICES[key]['price_usd']}", callback_data=f"buy_{key}"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu"))
    bot.send_message(message.chat.id, "🎫 اختر الفئة المناسبة لببجي موبايل:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "أكواد وبطاقات")
def show_codes_and_cards(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("Itunes USA 🍏", callback_data="view_itunes_sub")
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")
    markup.add(btn1, btn_back)
    bot.send_message(message.chat.id, "🎫 اختر فئة البطاقات المطلوبة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "view_itunes_sub")
def show_itunes_categories(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    keys = ["itunes_2usd", "itunes_3usd", "itunes_4usd", "itunes_5usd", "itunes_6usd", "itunes_7usd", "itunes_8usd", "itunes_9usd", "itunes_10usd", "itunes_15usd", "itunes_20usd", "itunes_25usd"]
    for k in keys:
        markup.add(types.InlineKeyboardButton(f"{PRICES[k]['name']} - ${PRICES[k]['price_usd']}", callback_data=f"buy_{k}"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع للخيارات", callback_data="back_to_cards_main"))
    bot.edit_message_text("🛍️ المنتجات المتاحة لبطاقات آيتونز:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["back_to_menu", "back_to_cards_main"])
def back_actions(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)

# ==========================================
# 5. نظام الشراء والخصم الفوري من المحفظة الرصيدية
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def ask_for_id(call):
    chat_id = call.message.chat.id
    product_key = call.data.replace("buy_", "")
    
    price_usd = PRICES[product_key]["price_usd"]
    price_local = round(price_usd * EXCHANGE_RATE, 2)
    
    # التحقق من أن العميل يمتلك رصيداً كافياً في محفظته لشراء المنتج فوراً
    user_balance = user_wallets.get(chat_id, 0.0)
    if user_balance < price_local:
        bot.send_message(chat_id, f"❌ رصيد محفظتك الحالي ({user_balance} ليرة) غير كافٍ لشراء هذا المنتج الذي قيمته ({price_local} ليرة).\nيرجى شحن رصيد محفظتك أولاً عبر زر 'شحن رصيد المحفظة 💰'.")
        return
        
    user_orders[chat_id] = {"product": product_key, "price_local": price_local}
    bot.delete_message(chat_id, call.message.message_id)
    
    msg = bot.send_message(chat_id, f"🎯 لشراء {PRICES[product_key]['name']} بقيمة {price_local} ليرة سورية من محفظتك.\nمن فضلك، أرسل رقم الآيدي (ID) الخاص بك الآن:")
    bot.register_next_step_handler(msg, process_wallet_purchase)

def process_wallet_purchase(message):
    chat_id = message.chat.id
    game_id_entered = message.text
    
    if chat_id in user_orders:
        info = user_orders[chat_id]
        product_key = info["product"]
        price_local = info["price_local"]
        
        # خصم المبلغ من المحفظة وحفظ الطلب بالأرشيف
        user_wallets[chat_id] -= price_local
        user_history[chat_id].append(f"شراء {PRICES[product_key]['name']} - بقيمة {price_local} ليرة [قيد المعالجة]")
        
        # إرسال الطلب فوراً للآدمن للموافقة والتسليم التلقائي عبر نمر كارد
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        btn_yes = types.InlineKeyboardButton("🟢 مقبول (تسليم نمر كارد)", callback_data=f"n_yes_{chat_id}_{product_key}_{game_id_entered}")
        btn_no = types.InlineKeyboardButton("🔴 مرفوض وإعادة الرصيد", callback_data=f"n_no_{chat_id}_{price_local}_{product_key}")
        admin_markup.add(btn_yes, btn_no)
        
        admin_text = (
            f"🛒 **عملية شراء جديدة بالخصم من المحفظة!**\n\n"
            f"👤 المشتري: (ID: {chat_id})\n"
            f"📦 المنتج: {PRICES[product_key]['name']}\n"
            f"🆔 الآيدي/البيانات: `{game_id_entered}`\n"
            f"💰 القيمة المخصومة: {price_local} ليرة"
        )
        bot.send_message(ADMIN_ID, admin_text, reply_markup=admin_markup, parse_mode="Markdown")
        bot.send_message(chat_id, "⏳ تم خصم القيمة من محفظتك بنجاح، ورفع الطلب للإدارة للتدقيق والشحن التلقائي فوراً!")

# ==========================================
# 6. نظام شحن رصيد المحفظة عبر تحويل شام كاش
# ==========================================
@bot.message_handler(func=lambda message: message.text == "شحن رصيد المحفظة 💰")
def deposit_money_request(message):
    msg = bot.send_message(message.chat.id, "💰 أرسل القيمة المراد شحنها بمحفظتك بالليرة السورية (مثال: 50000):")
    bot.register_next_step_handler(msg, process_deposit_step)

def process_deposit_step(message):
    chat_id = message.chat.id
    try:
        amount = float(message.text)
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("✅ قمت بالتحويل، أرسل للآدمن للموافقة", callback_data=f"dep_{chat_id}_{amount}")
        markup.add(btn)
        
        invoice = (
            f"💳 **طلب شحن رصيد المحفظة:**\n\n"
            f"💰 القيمة المحددة: {amount} ليرة سورية\n"
            f"📥 يرجى تحويل المبلغ إلى حساب شام كاش المعتمد التالي: `{SHAM_CASH_ACCOUNT}`\n\n"
