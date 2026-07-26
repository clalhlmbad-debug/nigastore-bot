import telebot
from telebot import types
import os

# --- الإعدادات الأساسية ---
TOKEN = "8826744317:AAHW1mreEvhIna70p0D0QOQ7-tKGH54yPXk"
ADMIN_ID = 8192730669
SHAM_CASH_ACCOUNT = "df910e178e027a6bfcae8b9b06b5384"

# سعر الصرف المعتمد (1 دولار = 145 ليرة سورية جديدة)
EXCHANGE_RATE = 145

bot = telebot.TeleBot(TOKEN)

user_orders = {}
ORDERS_FILE = "all_orders.txt"

# أسعار الفئات بالدولار لحساب السعر بالليرة السورية تلقائياً
PRICES = {
    "buy_pubg_60": 0.92,
    "buy_pubg_325": 4.59,
    "buy_pubg_660": 9.19,
    "buy_ff_110": 0.98,
    "buy_ff_231": 1.96
}

def save_order_to_file(order_details):
    with open(ORDERS_FILE, "a", encoding="utf-8") as f:
        f.write(order_details + "\n" + "-"*30 + "\n")

# --- قائمة الأوامر الترحيبية ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_games = types.InlineKeyboardButton("🎮 قسم الألعاب", callback_data="games_menu")
    btn_support = types.InlineKeyboardButton("👨‍💻 الدعم الفني", callback_data="support_menu")
    markup.add(btn_games, btn_support)
    
    if message.chat.id == ADMIN_ID:
        btn_admin = types.InlineKeyboardButton("📋 جميع الطلبات (خاص بالأدمن)", callback_data="admin_view_orders")
        markup.add(btn_admin)

    welcome_text = f"👋 أهلاً بك يا {message.from_user.first_name} في بوت Niga Store!\n\n📌 سعر الصرف المعتمد حالياً: 1$ = {EXCHANGE_RATE} ل.س\n\n🤖 الرجاء اختيار القسم الذي تريد تصفحه من الأزرار أدناه:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# --- معالجة الضغط على الأزرار الشفافة ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    if call.data == "games_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_pubg = types.InlineKeyboardButton("📱 ببجي موبايل", callback_data="pubg_info")
        btn_ff = types.InlineKeyboardButton("🔥 فري فاير", callback_data="ff_info")
        btn_back = types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")
        markup.add(btn_pubg, btn_ff, btn_back)
        bot.edit_message_text("🎮 مرحباً بك في قسم الألعاب! اختر لعبتك المفضلة:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "pubg_info":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"📦 60 UC - $0.92 ({round(0.92 * EXCHANGE_RATE)} ل.س)", callback_data="buy_pubg_60"),
            types.InlineKeyboardButton(f"📦 325 UC - $4.59 ({round(4.59 * EXCHANGE_RATE)} ل.س)", callback_data="buy_pubg_325"),
            types.InlineKeyboardButton(f"📦 660 UC - $9.19 ({round(9.19 * EXCHANGE_RATE)} ل.س)", callback_data="buy_pubg_660"),
            types.InlineKeyboardButton("🔙 العودة للألعاب", callback_data="games_menu")
        )
        bot.edit_message_text(f"📱 **PUBG MOBILE**\nسعر الصرف المعتمد: {EXCHANGE_RATE} ل.س\nاختر الفئة المناسبة من الأزرار أدناه:", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "ff_info":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(f"💎 110 Gems - $0.98 ({round(0.98 * EXCHANGE_RATE)} ل.س)", callback_data="buy_ff_110"),
            types.InlineKeyboardButton(f"💎 231 Gems - $1.96 ({round(1.96 * EXCHANGE_RATE)} ل.س)", callback_data="buy_ff_231"),
            types.InlineKeyboardButton("🔙 العودة للألعاب", callback_data="games_menu")
        )
        bot.edit_message_text(f"🔥 **Free Fire**\nسعر الصرف المعتمد: {EXCHANGE_RATE} ل.س\nاختر الفئة المناسبة لشحن جواهر فري فاير:", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "support_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_dev = types.InlineKeyboardButton("💬 تواصل مع المطور", url="https://t.me")
        btn_back = types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")
        markup.add(btn_dev, btn_back)
        bot.edit_message_text("👨‍💻 قسم الدعم الفني والمساعدة:\n\nإذا واجهتك أي مشكلة، يمكنك التواصل مع الإدارة مباشرة عبر الزر أدناه.", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "main_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_games = types.InlineKeyboardButton("🎮 قسم الألعاب", callback_data="games_menu")
        btn_support = types.InlineKeyboardButton("👨‍💻 الدعم الفني", callback_data="support_menu")
        markup.add(btn_games, btn_support)
        if chat_id == ADMIN_ID:
            markup.add(types.InlineKeyboardButton("📋 جميع الطلبات (خاص بالأدمن)", callback_data="admin_view_orders"))
        bot.edit_message_text("🤖 الرجاء اختيار القسم الذي تريد تصفحه من الأزرار أدناه:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("buy_pubg_") or call.data.startswith("buy_ff_"):
        game_type = "ببجي موبايل" if "pubg" in call.data else "فري فاير"
        unit = "UC" if "pubg" in call.data else "جوهرة"
        amount = call.data.split("_")[-1]
        
        price_in_usd = PRICES.get(call.data, 0.0)
        price_in_syr = round(price_in_usd * EXCHANGE_RATE)
        
        user_orders[call.from_user.id] = {
            "game": game_type,
            "amount": f"{amount} {unit}",
            "price_syr": price_in_syr,
            "step": "get_id"
        }
        
        bot.send_message(chat_id, f"🎮 الخاص بك في لعبة {game_type} الرجاء إدخال **الآيدي ID** الخاص بك:")
        bot.answer_callback_query(call.id)

    elif call.data == "admin_view_orders":
        if chat_id == ADMIN_ID:
            if os.path.exists(ORDERS_FILE) and os.path.getsize(ORDERS_FILE) > 0:
                with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                    orders_data = f.read()
                if len(orders_data) > 4000:
                    bot.send_message(chat_id, "📋 الطلبات كثيرة جداً، إليك الملف النصي الكامل للتحميل:")
                    with open(ORDERS_FILE, "rb") as f:
                        bot.send_document(chat_id, f)
                else:
                    bot.send_message(chat_id, f"📋 **جميع الطلبات المسجلة في المتجر:**\n\n{orders_data}")
            else:
                bot.send_message(chat_id, "📋 لا توجد أي طلبات مسجلة في المتجر حتى الآن!")
        else:
            bot.answer_callback_query(call.id, "❌ عذراً، هذا الزر مخصص لمالك البوت فقط!")

    # --- تم تعديل هذا الجزء بطريقة يدوية صريحة لمنع توقف السيرفر نهائياً ---
    elif call.data.startswith("accept_") or call.data.startswith("reject_"):
        if chat_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ عذراً، هذا الإجراء مخصص للآدمن فقط!")
            return
            
        data_parts = call.data.split("_")
        action = data_parts[0]
        target_user_id = data_parts[1]
        
        if action == "accept":
            bot.send_message(target_user_id, "✅ **تمت العملية بنجاح!**\n\nلقد تم التحقق من عملية الدفع وشحن حسابك بالألعاب بنجاح. شكراً لتعاملك معنا!")
            bot.edit_message_text(f"{call.message.text}\n\n🟢 **حالة الطلب:** تم الشحن بنجاح ✅", chat_id, call.message.message_id)
                
        elif action == "reject":
            bot.send_message(target_user_id, "❌ **عذراً، تم رفض طلبك!**\n\nلم يتم تأكيد عملية الشحن. يرجى التأكد من صحة رقم المعاملة أو التواصل مع الدعم الفني لحل المشكلة.")
            bot.edit_message_text(f"{call.message.text}\n\n🔴 **حالة الطلب:** تم الرفض وإشعار الزبون ❌", chat_id, call.message.message_id)
                
        bot.answer_callback_query(call.id)

# --- معالجة خطوات إدخال البيانات ---
@bot.message_handler(func=lambda message: message.from_user.id in user_orders)
def process_order_steps(message):
    user_id = message.from_user.id
    step = user_orders[user_id]["step"]
    
    if step == "get_id":
        user_orders[user_id]["player_id"] = message.text
        user_orders[user_id]["step"] = "get_payment"
        order_info = user_orders[user_id]
        
        payment_text = f"💰 **خطوة الدفع (الشام كاش):**\n\n" \
                       f"💵 المبلغ الإجمالي المطلوب: **{order_info['price_syr']} ليرة سورية جديدة**\n\n" \
                       f"يرجى إرسال مبلغ الفئة المطلوبة إلى عنوان الشام كاش التالي:\n" \
                       f"📌 العنوان: `{SHAM_CASH_ACCOUNT}`\n\n" \
                       f"⚠️ بعد إتمام التحويل، أرسل رقم المعاملة هنا لتأكيد طلبك:"
        bot.send_message(message.chat.id, payment_text, parse_mode="Markdown")
        
    elif step == "get_payment":
        user_orders[user_id]["transaction_id"] = message.text
        order_info = user_orders[user_id]
        
        success_text = f"✅ **تم استلام تفاصيل طلبك بنجاح!**\n\n🎮 اللعبة: {order_info['game']}\n📦 الفئة: {order_info['amount']}\n💰 القيمة المستحقة: {order_info['price_syr']} ل.س\n🆔 معرف اللاعب (ID): `{order_info['player_id']}`\n🧾 رقم المعاملة: `{order_info['transaction_id']}`\n\n⏳ جاري مراجعة طلبك خلال دقائق. شكراً لك!"
        bot.send_message(message.chat.id, success_text, parse_mode="Markdown")
        
        username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
        admin_notification = f"🚨 **طلب شحن جديد وصلك!**\n\n👤 الزبون: {username} (ID: {user_id})\n🎮 اللعبة: {order_info['game']}\n📦 الكمية: {order_info['amount']}\n💰 المبلغ المطلوب: {order_info['price_syr']} ل.س\n🆔 آيدي اللاعب: `{order_info['player_id']}`\n🧾 الرقم المرجعي: `{order_info['transaction_id']}`"
                             
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        btn_accept = types.InlineKeyboardButton("🟢 شحن (صح)", callback_data=f"accept_{user_id}")
        btn_reject = types.InlineKeyboardButton("🔴 رفض الطلب (خطأ)", callback_data=f"reject_{user_id}")
        admin_markup.add(btn_accept, btn_reject)
                             
