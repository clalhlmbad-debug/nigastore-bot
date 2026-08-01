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
# 2. مصفوفة قاعدة البيانات الوهمية (المحفظة والطلبات)
# ==========================================
# لتجنب تصفير المحفظة عند النوم المجاني لـ Render، ينصح لاحقاً بربط SQLite أو MongoDB.
db_users = {}   # الهيكل: {chat_id: {"balance": 0.0, "username": "", "orders": []}}
user_steps = {}  # لمتابعة خطوات الإدخال والطلبات المؤقتة لكل مستخدم

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

# خادم الويب للاستضافة المجانية
@app.route('/')
def home(): return "Bot system is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# دالة مساعدة لتسجيل المستخدمين الجدد
def check_user(user):
    if user.id not in db_users:
        db_users[user.id] = {
            "balance": 0, # الرصيد بالليرة السورية كاش
            "username": user.username if user.username else "لا يوجد",
            "orders": []
        }

# ==========================================
# 3. واجهة القائمة الرئيسية (الكيبورد السفلي المطابق تماماً)
# ==========================================
@bot.message_handler(commands=['start'])
def start_command(message):
    check_user(message.from_user)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    markup.add(types.KeyboardButton("PUBG MOBILE ⚡"), types.KeyboardButton("FREE FIRE 🔥"))
    markup.add(types.KeyboardButton("أكواد وبطاقات"), types.KeyboardButton("منتجات اخرى (تلقائي) 🎮"))
    markup.add(types.KeyboardButton("المنتجات اليدوية 🛍️"), types.KeyboardButton("حسابي 👤"))
    markup.add(types.KeyboardButton("طلباتي 📂"))
    markup.add(types.KeyboardButton("الدعم 📞"), types.KeyboardButton("تعليمات هامة ℹ️"))
    
    bot.send_message(message.chat.id, "👋 أهلاً بك في متجر الشحن الذكي الشامل!\nاستخدم الأزرار بالأسفل للتصفح والشحن الفوري:", reply_markup=markup)

# ==========================================
# 4. معالجة نقرات الكيبورد الرئيسي وقسم "حسابي" و "طلباتي"
# ==========================================
@bot.message_handler(func=lambda message: True)
def handle_reply_keyboard(message):
    chat_id = message.chat.id
    check_user(message.from_user)
    text = message.text
    
    if text == "PUBG MOBILE ⚡":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for k in ["pubg_60", "pubg_325", "pubg_660", "pubg_1800", "pubg_3850", "pubg_8100"]:
            markup.add(types.InlineKeyboardButton(f"{PRICES[k]['name']} - ${PRICES[k]['price_usd']}", callback_data=f"buy_{k}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu"))
        bot.send_message(chat_id, "🎫 اختر الفئة المناسبة لببجي موبايل:", reply_markup=markup)
        
    elif text == "أكواد وبطاقات":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("Itunes USA", callback_data="view_itunes_sub"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu"))
        bot.send_message(chat_id, "🎫 أقسام الأكواد والبطاقات الرقمية المتوفرة:", reply_markup=markup)
        
    elif text == "حسابي 👤":
        user_info = db_users[chat_id]
        balance_usd = round(user_info["balance"] / EXCHANGE_RATE, 2)
        profile_card = (
            f"👤 **بطاقة بيانات الحساب الخاصة بك:**\n\n"
            f"🆔 معرف الحساب التلغرام: `{chat_id}`\n"
            f"🏷️ اسم المستخدم: @{user_info['username']}\n"
            f"💰 رصيدك الكاش: **{user_info['balance']} ليرة سورية**\n"
            f"💵 ما يعادل بالدولار: {balance_usd} $\n\n"
            f"💡 يمكنك شحن وتعبئة محفظتك عبر الضغط على زر شحن الرصيد أدناه بالتحويل المباشر لشام كاش."
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ شحن الرصيد الآن", callback_data="deposit_funds"))
        bot.send_message(chat_id, profile_card, reply_markup=markup, parse_mode="Markdown")
        
    elif text == "طلباتي 📂":
        orders = db_users[chat_id]["orders"]
        if not orders:
            bot.send_message(chat_id, "📂 سجل فواتيرك فارغ، لم تقم بإجراء عمليات شراء بعد.")
            return
        log_text = "🗂️ **سجل عمليات الشراء والطلبات السابقة الخاصة بك:**\n\n"
        for idx, o in enumerate(orders[-7:], 1): # عرض آخر 7 طلبات للزبون
            log_text += f"{idx}️⃣ المنتج: {o['prod']} | الآيدي: `{o['id']}`\n💰 السعر: {o['price']} ليرة | الحالة: {o['status']}\n\n"
        bot.send_message(chat_id, log_text, parse_mode="Markdown")
        
    elif text == "الدعم 📞":
        bot.send_message(chat_id, f"🛠️ لقسم المساعدة المباشرة والاستفسارات تواصل مع الإدارة عبر المعرف: {ADMIN_ID}")
    elif text == "تعليمات هامة ℹ️":
        bot.send_message(chat_id, "⚠️ **تنبيهات للمشترين:**\n1. شحن المحفظة أولاً يضمن لك شراء المنتجات فوراً وتلقائياً دون انتظار موافقة الآدمن يدوياً.")

# ==========================================
# 5. تفريع واجهات آيتونز وزر الرجوع
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data in ["view_itunes_sub", "back_to_menu"])
def handle_navigation_callbacks(call):
    chat_id = call.message.chat.id
    if call.data == "view_itunes_sub":
        markup = types.InlineKeyboardMarkup(row_width=1)
        keys = ["itunes_2usd", "itunes_3usd", "itunes_4usd", "itunes_5usd", "itunes_6usd", "itunes_7usd", "itunes_8usd", "itunes_9usd", "itunes_10usd", "itunes_15usd", "itunes_20usd", "itunes_25usd"]
        for k in keys:
            markup.add(types.InlineKeyboardButton(f"{PRICES[k]['name']} - ${PRICES[k]['price_usd']}", callback_data=f"buy_{k}"))
        bot.edit_message_text("🛍️ المنتجات والبطاقات المتاحة لشام كاش ونمر كارد:", chat_id, call.message.message_id, reply_markup=markup)
    elif call.data == "back_to_menu":
        bot.delete_message(chat_id, call.message.message_id)

# ==========================================
# 6. نظام شحن وتعبئة رصيد المحفظة (Deposit System)
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data == "deposit_funds")
def start_deposit(call):
    chat_id = call.message.chat.id
    bot.delete_message(chat_id, call.message.message_id)
    msg = bot.send_message(chat_id, "💰 أرسل كمية الأموال المراد تعبئتها في محفظتك (بالليرة السورية كاش) مثال: `50000`:")
    bot.register_next_step_handler(msg, ask_deposit_receipt)

def ask_deposit_receipt(message):
    chat_id = message.chat.id
    try:
        amount = int(message.text)
        user_steps[chat_id] = {"deposit_amount": amount}
        msg = bot.send_message(chat_id, f"📥 من فضلك، قم بتحويل القيمة المستحقة المذكورة وهي **{amount} ليرة** لحساب شام كاش التالي: `{SHAM_CASH_ACCOUNT}`\n\nثم أرسل **رقم عملية الحوالة النصي أو صورة الإيصال** هنا لتأكيدها:")
        bot.register_next_step_handler(msg, send_deposit_to_admin)
    except:
        bot.send_message(chat_id, "❌ قيمة رقمية خاطئة، يرجى إعادة المحاولة والضغط على زر شحن الرصيد مجدداً.")

def send_deposit_to_admin(message):
    chat_id = message.chat.id
    receipt_data = message.text if message.text else "تم إرسال صورة إيصال بالتحويل المالي"
    amount = user_steps[chat_id]["deposit_amount"]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🟢 قبول الإيداع وإضافة الرصيد", callback_data=f"dep_yes_{chat_id}_{amount}"))
    markup.add(types.InlineKeyboardButton("🔴 رفض وثيقة التحويل", callback_data=f"dep_no_{chat_id}"))
    
    bot.send_message(ADMIN_ID, f"🔔 **إشعار طلب شحن محفظة جديد!**\n\n👤 المستخدم: (ID: {chat_id})\n💰 المبلغ المذكور: {amount} ليرة سورية\n📄 تفاصيل الإيصال: {receipt_data}", reply_markup=markup)
    bot.send_message(chat_id, "⏳ تم تسليم وثيقة شحن رصيد المحفظة بنجاح، جاري مطابقة كشف الحساب من قبل الآدمن وتأكيد رصيدك السحابي...")

# معالجة قرار الأدمن للإيداع المالي
@bot.callback_query_handler(func=lambda call: call.data.startswith("dep_"))
def process_admin_deposit(call):
    parts = call.data.split("_")
