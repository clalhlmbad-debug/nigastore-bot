import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8826744317:AAEhuJxpjx8m9il7rwvEJmca75qrJOvJ55M"
bot = telebot.TeleBot(TOKEN)

# عنوان الشام كاش الخاص بك (تم تحديثه)
SHAM_CASH_ACCOUNT = "df910e178e027a6bfcae8b99b06b5384"

# معرف حسابك التلغرام لإرسال الإشعارات والطلبات الجديدة إليك فوراً
ADMIN_ID = "8192730669"

# مخزن مؤقت لحفظ بيانات طلبات الزبائن قيد التنفيذ
user_orders = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("🎮 قسم الألعاب", callback_data="games_menu"),
        InlineKeyboardButton("🛠️ الدعم الفني", callback_data="support_menu")
    )
    welcome_text = f"🎯 أهلاً بك يا {message.from_user.first_name} في بوت Niga Store!\n\nالرجاء اختيار القسم الذي تريد تصفحه من الأزرار أدناه 👇"
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "games_menu":
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(
            InlineKeyboardButton("🔫 ببجي موبايل ⚡", callback_data="pubg_info"),
            InlineKeyboardButton("🔥 فري فاير 🔥", callback_data="ff_info"),
            InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🎮 مرحباً بك في قسم الألعاب! اختر لعبتك المفضلة:", reply_markup=markup)
    
    elif call.data == "pubg_info":
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(
            InlineKeyboardButton("💵 60 UC - $0.92", callback_data="buy_pubg_60"),
            InlineKeyboardButton("💵 325 UC - $4.59", callback_data="buy_pubg_325"),
            InlineKeyboardButton("💵 660 UC - $9.19", callback_data="buy_pubg_660"),
            InlineKeyboardButton("💵 1800 UC - $22.97", callback_data="buy_pubg_1800"),
            InlineKeyboardButton("💵 3850 UC - $45.94", callback_data="buy_pubg_3850"),
            InlineKeyboardButton("💵 8100 UC - $91.88", callback_data="buy_pubg_8100"),
            InlineKeyboardButton("🔙 رجوع", callback_data="games_menu")
        )
        pubg_text = "💳 **PUBG MOBILE** ⚡\n\n🔹 اختر الفئة المناسبة من الأزرار أدناه لتظهر لك التفاصيل:"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=pubg_text, parse_mode="Markdown", reply_markup=markup)
    
    elif call.data == "ff_info":
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(
            InlineKeyboardButton("💎 110 Gems - $0.98", callback_data="buy_ff_110"),
            InlineKeyboardButton("💎 231 Gems - $1.96", callback_data="buy_ff_231"),
            InlineKeyboardButton("💎 583 Gems - $4.91", callback_data="buy_ff_583"),
            InlineKeyboardButton("💎 1188 Gems - $9.82", callback_data="buy_ff_1188"),
            InlineKeyboardButton("💎 2420 Gems - $19.64", callback_data="buy_ff_2420"),
            InlineKeyboardButton("🔙 رجوع للخيارات", callback_data="games_menu")
        )
        ff_text = "🔥 **Free Fire (Auto) عروض** 🔥\n\n🔹 اختر الفئة المناسبة من الأزرار أدناه لتظهر لك التفاصيل:"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=ff_text, parse_mode="Markdown", reply_markup=markup)

    elif call.data.startswith("buy_pubg_") or call.data.startswith("buy_ff_"):
        game_type = "ببجي موبايل" if "pubg" in call.data else "فري فاير"
        unit = "UC" if "pubg" in call.data else "جوهرة"
        amount = call.data.split("_")[-1]
        
        user_orders[call.from_user.id] = {
            "game": game_type,
            "amount": f"{amount} {unit}",
            "step": "get_id"
        }
        
        bot.send_message(call.message.chat.id, f"📥 **الرجاء إدخال ID اللاعب** الخاص بك في لعبة {game_type}:")
        bot.answer_callback_query(call.id)

    elif call.data == "support_menu":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💬 تواصل مع المطور", url="https://t.me"), InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu"))
        support_text = "🛠️ **قسم الدعم الفني والمساعدة**\n\nإذا واجهتك أي مشكلة تواصل مباشرة مع الإدارة عبر الضغط على الزر أدناه."
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=support_text, parse_mode="Markdown", reply_markup=markup)
    
    elif call.data == "main_menu":
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton("🎮 قسم الألعاب", callback_data="games_menu"), InlineKeyboardButton("🛠️ الدعم الفني", callback_data="support_menu"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🎯 القائمة الرئيسية لبوت الخدمات. اختر قسماً من الأسفل:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.from_user.id in user_orders)
def process_order_steps(message):
    user_id = message.from_user.id
    step = user_orders[user_id]["step"]
    
    if step == "get_id":
        user_orders[user_id]["player_id"] = message.text
        user_orders[user_id]["step"] = "get_payment"
        
        payment_text = (
            f"💰 **خطوة الدفع (الشام كاش):**\n\n"
            f"يرجى إرسال مبلغ الفئة المطلوبة إلى عنوان الشام كاش التالي:\n"
            f"📌 العنوان: `{SHAM_CASH_ACCOUNT}`\n\n"
            f"⚠️ بعد إتمام التحويل، **أرسل رقم المعاملة أو الرقم المرجعي** هنا لتأكيد طلبك:"
        )
        bot.send_message(message.chat.id, payment_text, parse_mode="Markdown")
        
    elif step == "get_payment":
        user_orders[user_id]["transaction_id"] = message.text
        order_info = user_orders[user_id]
        
        # 1. إرسال رسالة تأكيد للزبون
        success_text = (
            "✅ **تم استلام تفاصيل طلبك بنجاح!**\n\n"
            f"🎮 اللعبة: {order_info['game']}\n"
            f"📦 الفئة: {order_info['amount']}\n"
            f"🆔 معرف اللاعب (ID): `{order_info['player_id']}`\n"
            f"🧾 رقم معاملة التحويل: `{order_info['transaction_id']}`\n\n"
            "⏳ جاري مراجعة عملية الدفع وشحن حسابك خلال دقائق معدودة. شكراً لثقتك بنا!"
        )
        bot.send_message(message.chat.id, success_text, parse_mode="Markdown")
        
        # 2. إرسال إشعار تلقائي وفوري لك (الأدمن) بوجود طلب شحن جديد مع كل التفاصيل
        admin_notification = (
            "🚨 **طلب شحن جديد وارد!** 🚨\n\n"
            f"👤 صاحب الطلب: {message.from_user.first_name} (@{message.from_user.username})\n"
            f"🎮 اللعبة: {order_info['game']}\n"
            f"📦 الفئة المطلوبة: {order_info['amount']}\n"
            f"🆔 معرف اللاعب (ID): `{order_info['player_id']}`\n"
            f"🧾 رقم المعاملة المرسل: `{order_info['transaction_id']}`\n\n"
            "💡 تأكد من وصول المبلغ إلى حساب الشام كاش الخاص بك ثم قم بالشحن للاعب."
        )
        try:
            bot.send_message(ADMIN_ID, admin_notification, parse_mode="Markdown")
        except Exception as e:
            print(f"فشل إرسال التنبيه للأدمن: {e}")
            
        del user_orders[user_id]

print("البوت يعمل الآن بنجاح مع أتمتة الدفع عبر عنوان الشام كاش وإرسال الطلبات للأدمن...")
bot.infinity_polling()
