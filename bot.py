import os
import uuid  # لتوليد معرف فريد لكل طلب كما تطلب وثائق نمر كارد
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

# إعدادات نمر كارد بناءً على الوثائق الرسمية
NEMER_API_TOKEN = "ضع_api_token_الخاص_بك_من_نمر_كارد"
BASE_URL = "https://nemer-card.com" # قم بتعديله إذا كان الرابط الأساسي لمتجرهم مختلفاً

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# مصفوفة الأسعار بناءً على الـ IDs المعتمدة في حسابك بنمر كارد
# قمت بوضع المعرفات 365 و 18 كأمثلة مأخوذة من الوثائق الخاصة بك
PRICES = {
    "pubg_60": {"price_usd": 0.92, "nemer_id": 365},
    "pubg_325": {"price_usd": 4.59, "nemer_id": 18}
}

user_orders = {}

# سيرفر الويب لإبقاء البوت مستيقظاً 24 ساعة على Render مجاناً
@app.route('/')
def home():
    return "Bot is Live and Running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# 2. القائمة الرئيسية وقسم الألعاب
# ==========================================
@bot.message_handler(commands=['start'])
def start_command(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_games = types.InlineKeyboardButton("🎮 قسم شحن ببجي موبايل", callback_data="cat_games")
    markup.add(btn_games)
    bot.send_message(message.chat.id, "👋 أهلاً بك في بوت الشحن السريع المتكامل!\nاضغط على الزر أدناه لبدء الطلب:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "cat_games")
def show_games(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    btn1 = types.InlineKeyboardButton(f"🔫 ببجي 60 شدة - {PRICES['pubg_60']['price_usd']} $", callback_data="buy_pubg_60")
    btn2 = types.InlineKeyboardButton(f"🔫 ببجي 325 شدة - {PRICES['pubg_325']['price_usd']} $", callback_data="buy_pubg_325")
    markup.add(btn1, btn2)
    bot.edit_message_text("🎮 اختر كمية الشدات المُراد شحنها لك:", chat_id, message_id, reply_markup=markup)

# ==========================================
# 3. خطوة طلب الآيدي (ID) من الزبون
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def ask_for_id(call):
    chat_id = call.message.chat.id
    product_key = call.data.replace("buy_", "")
    user_orders[chat_id] = {"product": product_key}
    
    bot.delete_message(chat_id, call.message.message_id)
    msg = bot.send_message(chat_id, "🎯 من فضلك، أرسل رقم الآيدي (ID) الخاص بحسابك في اللعبة الآن:")
    bot.register_next_step_handler(msg, process_payment_screen)

# ==========================================
# 4. حساب الفاتورة وتفاصيل تحويل شام كاش
# ==========================================
def process_payment_screen(message):
    chat_id = message.chat.id
    game_id_entered = message.text
    
    if chat_id in user_orders:
        user_orders[chat_id]["game_id"] = game_id_entered
        product_key = user_orders[chat_id]["product"]
        
        price_usd = PRICES[product_key]["price_usd"]
        price_local = round(price_usd * EXCHANGE_RATE, 2)
        user_orders[chat_id]["price_local"] = price_local
        
        markup = types.InlineKeyboardMarkup()
        btn_confirm = types.InlineKeyboardButton("✅ قمت بالتحويل، إرسال الطلب للمراجعة", callback_data="submit_order_to_admin")
        markup.add(btn_confirm)
        
        invoice_message = (
            f"🛒 **فاتورة الشراء المستخرجة بنجاح:**\n\n"
            f"📦 نوع الباقة: {product_key.upper().replace('_', ' ')}\n"
            f"🆔 آيدي حسابك: `{game_id_entered}`\n"
            f"💰 القيمة المطلوبة: **{price_local} ليرة سورية**\n\n"
            f"📌 **خطوات تحويل الأموال:**\n"
            f"الرجاء تحويل المبلغ الدقيق أعلاه إلى حساب شام كاش المعتمد التالي:\n"
            f"📥 الحساب: `{SHAM_CASH_ACCOUNT}`\n\n"
            f"⚠️ بعد إتمام إرسال الأموال، اضغط على الزر أدناه لتأكيد طلبك للآدمن."
        )
        bot.send_message(chat_id, invoice_message, reply_markup=markup, parse_mode="Markdown")

# ==========================================
# 5. ترحيل الطلب للآدمن (مقبول / مرفوض)
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data == "submit_order_to_admin")
def submit_to_admin(call):
    chat_id = call.message.chat.id
    
    if chat_id in user_orders:
        info = user_orders[chat_id]
        
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        btn_yes = types.InlineKeyboardButton("🟢 مقبول (شحن تلقائي نمر كارد)", callback_data=f"n_yes_{chat_id}_{info['product']}_{info['game_id']}")
        btn_no = types.InlineKeyboardButton("🔴 مرفوض", callback_data=f"n_no_{chat_id}")
        admin_markup.add(btn_yes, btn_no)
        
        admin_alert_text = (
            f"📩 **طلب شحن شدات جديد قيد المراجعة!**\n\n"
            f"👤 المشتري: @{call.from_user.username} (ID: {chat_id})\n"
            f"📦 الباقة: {info['product'].upper()}\n"
            f"🆔 آيدي اللاعب: `{info['game_id']}`\n"
            f"💰 القيمة بـ شام كاش: {info['price_local']} ليرة"
        )
        bot.send_message(ADMIN_ID, admin_alert_text, reply_markup=admin_markup, parse_mode="Markdown")
        bot.edit_message_text("⏳ تم إرسال معلومات طلبك والآيدي بنجاح لمراجعة الإدارة وتدقيق الحساب المالي...", chat_id, call.message.message_id)

# ==========================================
# 6. تنفيذ الشحن الفوري عبر API نمر كارد عند ضغط القبول
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("n_"))
def handle_nimer_card_shipping(call):
    data_split = call.data.split("_")
    action = data_split
    customer_chat_id = int(data_split)
    
    if action == "yes":
        product_key = f"{data_split}_{data_split}"
        player_game_id = data_split
        
        # جلب الـ ID الخاص بالمنتج من مصفوفة الأسعار
        product_id = PRICES[product_key]["nemer_id"]
        # توليد UUIDv4 فريد تطلبه الوثائق لتجنب تكرار الطلب
        order_uuid = str(uuid.uuid4()) 
        
        # تجهيز رابط نمر كارد حسب التوثيق الرسمي المرسل
        # الرابط: /client/api/newOrder/{product_id}/params
        api_url = f"{BASE_URL}/client/api/newOrder/{product_id}/params"
        
        # رأس المصادقة المطلوبة (api-token)
        headers = {
            "api-token": NEMER_API_TOKEN,
            "Content-Type": "application/json"
        }
        
        # البيانات المرسلة بجسم الطلب (POST) حسب الوثائق
        payload = {
            "qty": 1,
            "playerId": player_game_id,
            "order_uuid": order_uuid
        }
        
        try:
            # إرسال الطلب البرمجي الفوري لخادم نمر كارد
            response = requests.post(api_url, headers=headers, json=payload, timeout=12)
            res_data = response.json()
            
            # التحقق من استجابة نمر كارد الناجحة ("status": "OK") والقبول ("accept")
            if response.status_code == 200 and res_data.get("status") == "OK":
                order_status = res_data.get("data", {}).get("status")
                
                if order_status == "accept":
                    bot.send_message(customer_chat_id, f"🥳 **تهانينا! تم تأكيد الدفع وشحن الـ ({product_key.upper().replace('_', ' ')}) تلقائياً لحسابك بنجاح عبر نمر كارد!**")
                    bot.edit_message_text(call.message.text + "\n\n✅ **حالة الطلب: تم القبول والشحن التلقائي عبر نمر كارد.**", ADMIN_ID, call.message.message_id)
                elif order_status == "wait":
                    bot.send_message(customer_chat_id, "⏳ تم قبول طلبك، وهو الآن في قائمة الانتظار لدى نمر كارد وسيصلك الشحن فوراً.")
                    bot.edit_message_text(call.message.text + "\n\n⏳ **حالة الطلب: في الانتظار (Wait) على نمر كارد.**", ADMIN_ID, call.message.message_id)
                else:
                    bot.send_message(ADMIN_ID, "⚠️ تم رفض الطلب من قِبل سيرفر نمر كارد، يرجى الشحن يدوياً.")
                    bot.send_message(customer_chat_id, "⏳ نعتذر، هناك تحديث مؤقت في نظام الشحن، جاري تسليم طلبك يدوياً بواسطة الإدارة خلال دقائق.")
            else:
                bot.send_message(ADMIN_ID, f"❌ فشل الاتصال بنمر كارد. كود الخطأ: {response.status_code}")
                bot.send_message(customer_chat_id, "⏳ تم تأكيد دفعتك، وجاري تسليم الشدات لحسابك يدوياً الآن.")
                
        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ حدث خطأ برمي أثناء الاتصال بنمر كارد: {e}")
            bot.send_message(customer_chat_id, "⏳ تم استلام الدفع، وجاري الشحن يدوياً فوراً.")
            
    elif action == "no":
        bot.send_message(customer_chat_id, "❌ **نعتذر منك، تم رفض طلبك من قبل الإدارة لعدم مطابقة بيانات تحويل شام كاش.**")
        bot.edit_message_text(call.message.text + "\n\n❌ **حالة الطلب: تم الرفض والإلغاء من قبل الآدمن.**", ADMIN_ID, call.message.message_id)

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling()
