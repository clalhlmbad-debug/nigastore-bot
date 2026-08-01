import os
import uuid
import telebot
from telebot import types
from flask import Flask
from threading import Thread
import requests

# ==========================================
# 1. الإعدادات الأساسية
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
# 2. مصفوفة الأسعار والـ IDs المحدثة لآيتونز وببجي
# ==========================================
# يرجى مراجعة لوحة تحكم نمر كارد لوضع الـ nemer_id الصحيح لكل فئة
PRICES = {
    # باقات ببجي موبايل
    "pubg_60": {"name": "60 UC", "price_usd": 0.92, "nemer_id": 365},
    "pubg_325": {"name": "325 UC", "price_usd": 4.59, "nemer_id": 18},
    "pubg_660": {"name": "660 UC", "price_usd": 9.19, "nemer_id": 103},
    "pubg_1800": {"name": "1800 UC", "price_usd": 22.97, "nemer_id": 104},
    "pubg_3850": {"name": "3850 UC", "price_usd": 45.94, "nemer_id": 105},
    "pubg_8100": {"name": "8100 UC", "price_usd": 91.88, "nemer_id": 106},
    
    # فئات بطاقات آيتونز الخمس المحددة والمطلوبة فقط
    "itunes_2usd": {"name": "Itunes 2$ US GiftCard", "price_usd": 1.98, "nemer_id": 301},
    "itunes_5usd": {"name": "Itunes 5$ US GiftCard", "price_usd": 4.96, "nemer_id": 304},
    "itunes_10usd": {"name": "Itunes 10$ US GiftCard", "price_usd": 9.92, "nemer_id": 309},
    "itunes_20usd": {"name": "Itunes 20$ US GiftCard", "price_usd": 19.84, "nemer_id": 311},
    "itunes_50usd": {"name": "Itunes 50$ US GiftCard", "price_usd": 49.50, "nemer_id": 315}  # اضبط السعر والـ ID بدقة
}

user_wallets = {}  
user_orders_history = {}  
user_orders = {}  

@app.route('/')
def home():
    return "Bot is Live and Running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

def init_user(chat_id):
    if chat_id not in user_wallets:
        user_wallets[chat_id] = 0.0  
    if chat_id not in user_orders_history:
        user_orders_history[chat_id] = []

# ==========================================
# 3. واجهة القائمة الرئيسية
# ==========================================
@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    init_user(chat_id)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn_pubg = types.KeyboardButton("PUBG MOBILE ⚡")
    btn_ff = types.KeyboardButton("FREE FIRE 🔥")
    btn_codes = types.KeyboardButton("أكواد وبطاقات")
    btn_other = types.KeyboardButton("منتجات اخرى (تلقائي) 🎮")
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
    
    bot.send_message(chat_id, "⬇️ القائمة الرئيسية لمتجر GG Store ⬇️", reply_markup=markup)

# ==========================================
# 4. محفظة حسابي وشحن الرصيد
# ==========================================
@bot.message_handler(func=lambda message: message.text == "حسابي 👤")
def show_my_account(message):
    chat_id = message.chat.id
    init_user(chat_id)
    
    balance = user_wallets[chat_id]
    balance_usd = round(balance / EXCHANGE_RATE, 2)
    
    markup = types.InlineKeyboardMarkup()
    btn_deposit = types.InlineKeyboardButton("➕ شحن رصيد المحفظة عبر شام كاش", callback_data="wallet_deposit")
    markup.add(btn_deposit)
    
    profile_text = (
        f"👤 **لوحة التحكم بحسابك الشخصي:**\n\n"
        f"🆔 معرف الحساب (ID): `{chat_id}`\n"
        f"💰 رصيدك الحالي: **{balance} ليرة سورية**\n"
        f"💵 ما يعادله بالدولار: {balance_usd} $\n"
        f"📈 سعر الصرف المعتمد: {EXCHANGE_RATE} ليرة / $\n\n"
        f"يمكنك الشحن الفوري لمحفظتك لتنفيذ طلباتك برمشة عين تلقائياً!"
    )
    bot.send_message(chat_id, profile_text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "طلباتي 📂")
def show_my_orders(message):
    chat_id = message.chat.id
    init_user(chat_id)
    
    orders = user_orders_history[chat_id]
    if not orders:
        bot.send_message(chat_id, "📂 لا توجد أي طلبات سابقة مسجلة في حسابك حتى الآن.")
        return
        
    history_text = "📂 **سجل عمليات الشراء الخاصة بك:**\n\n"
    for idx, ord_item in enumerate(orders[-5:], 1): 
        history_text += f"{idx}️⃣ المنتج: {ord_item['name']} | السعر: {ord_item['price']} ليرة | الحالة: ✅ ناجح\n"
    bot.send_message(chat_id, history_text)

@bot.callback_query_handler(func=lambda call: call.data == "wallet_deposit")
def wallet_deposit_start(call):
    chat_id = call.message.chat.id
    bot.delete_message(chat_id, call.message.message_id)
    msg = bot.send_message(chat_id, "💰 أرسل القيمة التي ترغب في شحنها بمحفظتك (بالليرة السورية فقط، أرقام فقط):")
    bot.register_next_step_handler(msg, process_deposit_amount)

def process_deposit_amount(message):
    chat_id = message.chat.id
    amount_text = message.text
    
    if not amount_text.isdigit():
        bot.send_message(chat_id, "❌ خطأ، يرجى إرسال رقم صحيح. أعد المحاولة من خلال قسم حسابي.")
        return
        
    amount = float(amount_text)
    markup = types.InlineKeyboardMarkup()
    btn_confirm = types.InlineKeyboardButton("✅ قمت بالتحويل، أرسل الإيصال للأدمن", callback_data=f"dep_submit_{amount}")
    markup.add(btn_confirm)
    
    deposit_invoice = (
        f"💳 **طلب شحن رصيد المحفظة:**\n\n"
        f"💰 المبلغ المطلوب شحنه: **{amount} ليرة سورية**\n"
        f"📥 يرجى تحويل القيمة الدقيقة إلى حساب شام كاش: `{SHAM_CASH_ACCOUNT}`\n\n"
        f"⚠️ اضغط على الزر بالأسفل بعد التحويل مباشرة ليتم مراجعة دفعتك وإضافة الرصيد لحسابك."
    )
    bot.send_message(chat_id, deposit_invoice, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("dep_submit_"))
def submit_deposit_to_admin(call):
    chat_id = call.message.chat.id
    amount = call.data.replace("dep_submit_", "")
    
    admin_markup = types.InlineKeyboardMarkup()
    btn_accept = types.InlineKeyboardButton("🟢 تأكيد وإضافة الرصيد", callback_data=f"ad_dep_yes_{chat_id}_{amount}")
    btn_reject = types.InlineKeyboardButton("🔴 رفض عملية الشحن", callback_data=f"ad_dep_no_{chat_id}")
    admin_markup.add(btn_accept, btn_reject)
    
    admin_msg = (
        f"💰 **إشعار طلب شحن محفظة جديد!**\n\n"
        f"👤 المستخدم: (ID: {chat_id})\n"
        f"💵 القيمة المطلوب شحنها: **{amount} ليرة سورية**\n"
        f"قم بمراجعة حساب شام كاش للتأكد من وصول المبلغ، ثم اضغط على تأكيد الرصيد."
    )
    bot.send_message(ADMIN_ID, admin_msg, reply_markup=admin_markup)
    bot.edit_message_text("⏳ تم إرسال إشعار الدفع للإدارة، سيتم مراجعة حساب شام كاش وإضافة الرصيد لمحفظتك فوراً.", chat_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ad_dep_"))
def handle_admin_deposit_decision(call):
    data = call.data.replace("ad_dep_", "").split("_")
    action = data[0]
    customer_id = int(data[1])
    
    if action == "yes":
        amount = float(data[2])
        init_user(customer_id)
        user_wallets[customer_id] += amount
        bot.send_message(customer_id, f"🥳 **تهانينا! وافقت الإدارة على شحنتك المادية، وتمت إضافة {amount} ليرة سورية إلى محفظتك بنجاح!**")
        bot.edit_message_text(call.message.text + "\n\n✅ **تمت إضافة الرصيد للمحفظة بنجاح.**", ADMIN_ID, call.message.message_id)
    else:
        bot.send_message(customer_id, "❌ **للأسف، تم رفض طلب شحن المحفظة من قبل الإدارة لعدم مطابقة بيانات الدفع.**")
        bot.edit_message_text(call.message.text + "\n\n❌ **تم الرفض والإلغاء.**", ADMIN_ID, call.message.message_id)

# ==========================================
# 5. معالجة تصفح باقات الألعاب وبطاقات آيتونز الخمس
# ==========================================
@bot.message_handler(func=lambda message: message.text == "PUBG MOBILE ⚡")
def show_pubg_packages(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_60 = types.InlineKeyboardButton(f"60 UC - ${PRICES['pubg_60']['price_usd']}", callback_data="buy_pubg_60")
    btn_325 = types.InlineKeyboardButton(f"325 UC - ${PRICES['pubg_325']['price_usd']}", callback_data="buy_pubg_325")
    btn_660 = types.InlineKeyboardButton(f"660 UC - ${PRICES['pubg_660']['price_usd']}", callback_data="buy_pubg_660")
    btn_1800 = types.InlineKeyboardButton(f"1800 UC - ${PRICES['pubg_1800']['price_usd']}", callback_data="buy_pubg_1800")
    btn_3850 = types.InlineKeyboardButton(f"3850 UC - ${PRICES['pubg_3850']['price_usd']}", callback_data="buy_pubg_3850")
    btn_8100 = types.InlineKeyboardButton(f"8100 UC - ${PRICES['pubg_8100']['price_usd']}", callback_data="buy_pubg_8100")
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")
    
    markup.add(btn_60, btn_325, btn_660, btn_1800, btn_3850, btn_8100, btn_back)
    bot.send_message(message.chat.id, "🎫 اختر الفئة المناسبة لببجي:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "أكواد وبطاقات")
def show_codes_and_cards(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("Itunes USA", callback_data="view_itunes_sub")
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")
    markup.add(btn1, btn_back)
    bot.send_message(message.chat.id, "🎫 اختر الصنف المطلوب:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "view_itunes_sub")
def show_itunes_categories(call):
    chat_id = call.message.chat.id
