import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8826744317:AAEhuJxpjx8m9il7rwvEJmca75qrJOvJ55M"
bot = telebot.TeleBot(TOKEN)

# عنوان الشام كاش الخاص بك
SHAM_CASH_ACCOUNT = "df910e178e027a6bfcae8b99b06b5384"

# معرف حسابك التلغرام لإرسال الإشعارات والطلبات الجديدة إليك فوراً
ADMIN_ID = "8192730669"

# مخزن مؤقت لحفظ بيانات طلبات الزبائن قيد التنفيذ
user_orders = {}

# القائمة الرئيسية عند إرسال /start أو الضغط على زر الرئيسية
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # 1. إنشاء الأزرار السفلية الثابتة (مثل الصورة تماماً)
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.row(KeyboardButton("PUBG MOBILE ⚡"), KeyboardButton("FREE FIRE 🔥"))
    reply_markup.row(KeyboardButton("أكواد وبطاقات"), KeyboardButton("منتجات اخرى (تلقائي) 🎮"))
    reply_markup.row(KeyboardButton("المنتجات اليدوية 🛍️"), KeyboardButton("حسابي 👤"))
    reply_markup.row(KeyboardButton("طلباتي 📂"), KeyboardButton("الدعم 📞"), KeyboardButton("تعليمات هامة ℹ️"))

    # 2. إنشاء الأزرار الشفافة التفاعلية تحت الرسالة الأولى
    inline_markup = InlineKeyboardMarkup()
    inline_markup.row(InlineKeyboardButton("⚡ إيداع اوتو ⚡", callback_data="deposit_auto"))
    inline_markup.row(InlineKeyboardButton("💳 إيداع يدوي 💳", callback_data="deposit_manual"))

    welcome_text = (
        f"👤 **ملفك الشخصي**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"▫️ المعرف: @{message.from_user.username if message.from_user.username else 'لا يوجد'}\n"
        f"▫️ الآيدي: `{message.from_user.id}`\n\n"
        f"👑 رصيدك الحالي: $0.02\n"
        f"📅 مصروفات آخر 30 يوم: $0.00\n"
        f"📊 نسبة الخصم الحالية: 0%"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=reply_markup)
    bot.send_message(message.chat.id, "👇 اختر أحد خيارات الإيداع أدناه أو تصفح القائمة السفلية:", reply_markup=inline_markup)

# التعامل مع الأزرار السفلية الثابتة عند الضغط عليها
@bot.message_handler(func=lambda message: True)
def handle_reply_keyboard(message):
    if message.text == "PUBG MOBILE ⚡":
        trigger_pubg(message.chat.id)
    elif message.text == "FREE FIRE 🔥":
        trigger_free_fire(message.chat.id)
    elif message.text == "الدعم 📞":
        trigger_support(message.chat.id)
    elif message.text in ["أكواد وبطاقات", "منتجات اخرى (تلقائي) 🎮", "المنتجات اليدوية 🛍️", "حسابي 👤", "طلباتي 📂", "تعليمات هامة ℹ️"]:
        bot.send_message(message.chat.id, f"⚙️ قسم **{message.text}** قيد التطوير حالياً وسيتم تفعيله قريباً.")

# معالجة الأزرار الشفافة (Inline)
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "games_menu":
        # إعادة توجيههم لرسالة ترحيبية بالقائمة الرئيسية
        send_welcome(call.message)
    
    elif call.data == "pubg_info":
        trigger_pubg(call.message.chat.id, call.message.message_id)
        
    elif call.data == "ff_info":
        trigger_free_fire(call.message.chat.id, call.message.message_id)

    elif call.data == "support_menu":
        trigger_support(call.message.chat.id, call.message.message_id)

    # معالجة طلبات الشراء
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

# وظائف مساعدة لعرض القوائم لمنع تكرار الكود
def trigger_pubg(chat_id, message_id=None):
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
    text = "💳 **PUBG MOBILE** ⚡\n\n🔹 اختر الفئة المناسبة من الأزرار أدناه لتظهر لك التفاصيل:"
    if message_id:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

def trigger_free_fire(chat_id, message_id=None):
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
    text = "🔥 **Free Fire (Auto) عروض** 🔥\n\n🔹 اختر الفئة المناسبة من الأزرار أدناه لتظهر لك التفاصيل:"
    if message_id:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

def trigger_support(chat_id, message_id=None):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💬 تواصل مع المطور", url="https://t.me"))
    text = (
        "📬 **تواصل مع الدعم في حال واجهت أي مشاكل**\n\n"
        "🔹 حساب الدعم : @nigastor\n\n"
        "📢 لمتابعة اخر التحديثات والعروض\n\n"
        "🔹 قناة البوت : @GGStoreSy"
    )
    if message_id:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

# استقبال رسائل الزبون النصية (الـ ID ورقم المعاملة)
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
        
        success_text = (
            "✅ **تم استلام تفاصيل طلبك بنجاح!**\n\n"
            f"🎮 اللعبة: {order_info['game']}\n"
            f"📦 الفئة: {order_info['amount']}\n"
            f"🆔 معرف اللاعب (ID): `{order_info['player_id']}`\n"
            f"🧾 رقم معاملة التحويل: `{order_info['transaction_id']}`\n\n"
            "⏳ جاري مراجعة عملية الدفع وشحن حسابك خلال دقائق معدودة. شكراً لثقتك بنا!"
        )
        bot.send_message(message.chat.id, success_text, parse_mode="Markdown")
        
        admin_notification = (
            "🚨 **طلب شحن جديد وارد!** 🚨\n\n"
            f"👤 صاحب الطلب: {message.from_user.first_name} (@{message.from_user.username})\n"
            f"🎮 اللعبة: {order_info['game']}\n"
            f"📦 الفئة المطلوبة: {order_info['amount']}\n"
            f"🆔 معرف اللاعب (ID): `{order_info['player_id']}`\n"
            f"🧾 رقم المعاملة المرسل: `{order_info['transaction_id']}`\n\n"
            "💡 تأكد من وصول المبلغ ثم قم بالشحن للاعب."
        )
        try:
            bot.send_message(ADMIN_ID, admin_notification, parse_mode="Markdown")
        except Exception as e:
            print(f"فشل التنبيه: {e}")
            
        del user_orders[user_id]

print("البوت يعمل بالقوائم المطابقة للصورة الجديدة تماماً...")
bot.infinity_polling()
