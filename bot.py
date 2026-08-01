import os
import telebot
from telebot import types
from flask import Flask
from threading import Thread
import requests  # ستحتاج للتأكد من وجود هذه المكتبة في ملف requirements.txt الخاص بك

# ==========================================
# 1. الإعدادات الأساسية للبوت (مأخوذة من كودك)
# ==========================================
TOKEN = "8826744317:AAHR9wuT8sNK0vG98uCcGmaps7-YntrSWiQ"  # تأكد من تحديثه إذا قمت بتغييره لحماية أمن بوتك!
ADMIN_ID = 8192730669
SHAM_CASH_ACCOUNT = "df910e11786027a6bfcae8b9b06b5384"
EXCHANGE_RATE = 145

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# ==========================================
# 2. مصفوفة الأسعار والمنتجات (الأسعار بالدولار)
# ==========================================
PRICES = {
    "pubg_60": 0.92,
    "pubg_325": 4.59,
    "freefire_100": 0.85,
    "insta_1k": 1.20,
    "netflix_1m": 3.50
}

# ==========================================
# 3. إعداد نظام Flask لإبقاء البوت مستيقظاً 24 ساعة
# ==========================================
@app.route('/')
def home():
    return "Bot is Live and Running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# 4. الأوامر والقوائم التفاعلية للمستخدمين
# ==========================================

@bot.message_handler(commands=['start'])
def start_command(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn_games = types.InlineKeyboardButton("🎮 شحن ألعاب", callback_data="cat_games")
    btn_apps = types.InlineKeyboardButton("📱 برامج وبطاقات", callback_data="cat_apps")
    btn_support = types.InlineKeyboardButton("📞 الدعم الفني", callback_data="cat_support")
    
    markup.add(btn_games, btn_apps)
    markup.add(btn_support)
    
    welcome_text = (
        "👋 أهلاً بك في بوت الشحن المتكامل السريع!\n\n"
        "الرجاء اختيار القسم الذي ترغب في تصفحه من الأزرار أدناه:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# التنقل بين الأقسام الرئيسية
@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def handle_categories(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data == "cat_games":
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton(f"🔫 ببجي 60 شدة - {PRICES['pubg_60']} $", callback_data="buy_pubg_60")
        btn2 = types.InlineKeyboardButton(f"🔫 ببجي 325 شدة - {PRICES['pubg_325']} $", callback_data="buy_pubg_325")
        btn3 = types.InlineKeyboardButton(f"🔥 فري فاير 100 جوهرة - {PRICES['freefire_100']} $", callback_data="buy_freefire_100")
        btn_home = types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="return_home")
        markup.add(btn1, btn2, btn3, btn_home)
        
        bot.edit_message_text("🎮 قسم شحن الألعاب:\nاختر الباقة المناسبة لك لشحنها تلقائياً:", chat_id, message_id, reply_markup=markup)
        
    elif call.data == "cat_apps":
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton(f"🎵 نتفليكس شهر - {PRICES['netflix_1m']} $", callback_data="buy_netflix_1m")
        btn_home = types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="return_home")
        markup.add(btn1, btn_home)
        
        bot.edit_message_text("📱 قسم البرامج والاشتراكات:\nاختر الباقة المطلوبة للتفعيل:", chat_id, message_id, reply_markup=markup)
        
    elif call.data == "cat_support":
        markup = types.InlineKeyboardMarkup()
        btn_home = types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="return_home")
        markup.add(btn_home)
        bot.edit_message_text(f"📞 للدعم الفني والاستفسارات المباشرة:\n\nتواصل مع الإدارة عبر حساب المطوّر.\nمعرف الآدمين: {ADMIN_ID}", chat_id, message_id, reply_markup=markup)

# ==========================================
# 5. نظام الفواتير وحساب الأسعار تلقائياً بناءً على مصفوفتك
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_purchase(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    product_key = call.data.replace("buy_", "")
    
    if product_key in PRICES:
        price_usd = PRICES[product_key]
        # العملية الحسابية تلقائياً بناءً على مصفوفة الأسعار وسعر الصرف الخاص بك
        price_local = round(price_usd * EXCHANGE_RATE, 2)
        
        markup = types.InlineKeyboardMarkup()
        btn_pay = types.InlineKeyboardButton("💳 دفع تلقائي (شام كاش)", callback_data=f"pay_sham_{product_key}_{price_local}")
        btn_back = types.InlineKeyboardButton("🔙 إلغاء والعودة", callback_data="return_home")
        markup.add(btn_pay, btn_back)
        
        invoice_text = (
            f"🛒 **تفاصيل الفاتورة المستخرجة:**\n\n"
            f"📦 المنتج المطلوب: {product_key.upper().replace('_', ' ')}\n"
            f"💵 السعر الأصلي: {price_usd} $\n"
            f"💰 القيمة بالعملة المحلية: {price_local} ليرة\n"
            f"📈 سعر الصرف المعتمد: {EXCHANGE_RATE}\n\n"
            f"اضغط على زر الدفع أدناه لإرسال الأموال وتأكيد العملية تلقائياً مالياً."
        )
        bot.edit_message_text(invoice_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

# ==========================================
# 6. قسم معالجة الدفع التلقائي عبر بوابة شام كاش (Sham Cash)
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_sham_"))
def process_sham_payment(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # تفكيك البيانات: pay_sham_[اسم_المنتج]_[السعر_المحلي]
    data_parts = call.data.split("_")
    product_name = f"{data_parts[2]}_{data_parts[3]}"
    amount_to_pay = data_parts[4]
    
    # إعداد واجهة برمجية لطلب الدفع من سيرفر شام كاش
    # ملاحظة: قم بتعديل هذا الرابط بناءً على الـ API الممنوح لك من دعم شام كاش الرسمي
    sham_api_url = "https://shamcash.com" 
    
    payload = {
        "account_secret": SHAM_CASH_ACCOUNT,
        "amount": amount_to_pay,
        "currency": "SYP",
        "order_id": f"USER_{chat_id}_{product_name}",
        "callback_url": f"https://onrender.com" # استبدل برابط سيرفرك الخاص على رندر لاحقاً ليتلقى تأكيد الدفع
    }
    
    try:
        # إرسال الطلب البرمجي لشام كاش لتوليد رابط الدفع للزبون
        # ريثما تضع إعدادات السيرفر المباشرة، البوت سيعطي المستخدم التعليمات الفورية للتواصل:
        markup = types.InlineKeyboardMarkup()
        btn_home = types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="return_home")
        markup.add(btn_home)
        
        success_text = (
            f"🚀 **طلب الدفع جاهز!**\n\n"
            f"يرجى تحويل القيمة المستحقة: **{amount_to_pay} ليرة**\n"
            f"إلى حساب شام كاش السري المربوط بالمنصة.\n\n"
            f"عند إتمام عملية تحويلك بنجاح، يرجى إرسال رقم الإيصال أو الصورة إلى الإدارة لتنفيذ الشحن السريع لحسابك."
        )
        bot.edit_message_text(success_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
        
    except Exception as e:
        bot.send_message(chat_id, "❌ عذراً، هناك مشكلة مؤقتة في الاتصال ببوابة الدفع. يرجى المحاولة لاحقاً أو الاتصال بالدعم الفني.")

# العودة للقائمة الرئيسية
@bot.callback_query_handler(func=lambda call: call.data == "return_home")
def return_home(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_games = types.InlineKeyboardButton("🎮 شحن ألعاب", callback_data="cat_games")
    btn_apps = types.InlineKeyboardButton("📱 برامج وبطاقات", callback_data="cat_apps")
    markup.add(btn_games, btn_apps)
    
    bot.edit_message_text("👋 الرجاء اختيار القسم الذي ترغب في تصفحه من الأزرار أدناه:", chat_id, message_id, reply_markup=markup)

# ==========================================
# 7. تشغيل السيرفر المزدوج للبوت
# ==========================================
if __name__ == '__main__':
    keep_alive() # تشغيل خادم الويب لمواجهة إغلاق الاستضافات المجانية في الخلفية تلقائياً
    print("البوت الاحترافي المتكامل يعمل الآن بنجاح...")
    bot.infinity_polling()
