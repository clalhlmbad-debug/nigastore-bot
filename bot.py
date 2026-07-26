import telebot
from telebot import types
import os

# --- الإعدادات الأساسية ---
TOKEN = "8826744317:AAHW1mreEvhIna70p0D0QOQ7-tKGH54yPXk"
ADMIN_ID = 8192730669
SHAM_CASH_ACCOUNT = "df910e178e027a6bfcae8b9b06b5384"

bot = telebot.TeleBot(TOKEN)

# مخزن مؤقت لحالات طلبات الزبائن الحالية
user_orders = {}
# اسم الملف النصي لحفظ جميع الطلبات بشكل دائم لزر الأدمن
ORDERS_FILE = "all_orders.txt"

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
    
    # إذا كان المرسل هو الأدمن (أنت)، يظهر زر إضافي لرؤية كافة الطلبات
    if message.chat.id == ADMIN_ID:
        btn_admin = types.InlineKeyboardButton("📋 جميع الطلبات (خاص بالأدمن)", callback_data="admin_view_orders")
        markup.add(btn_admin)

    welcome_text = f"👋 أهلاً بك يا {message.from_user.first_name} في بوت Niga Store!\n\n🤖 الرجاء اختيار القسم الذي تريد تصفحه من الأزرار أدناه:"
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
            types.InlineKeyboardButton("📦 60 UC - $0.92", callback_data="buy_pubg_60"),
            types.InlineKeyboardButton("📦 325 UC - $4.59", callback_data="buy_pubg_325"),
            types.InlineKeyboardButton("📦 660 UC - $9.19", callback_data="buy_pubg_660"),
            types.InlineKeyboardButton("🔙 العودة للألعاب", callback_data="games_menu")
        )
        bot.edit_message_text("📱 **PUBG MOBILE**\nاختر الفئة المناسبة من الأزرار أدناه لتظهر لك التفاصيل:", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "ff_info":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("💎 110 Gems - $0.98", callback_data="buy_ff_110"),
            types.InlineKeyboardButton("💎 231 Gems - $1.96", callback_data="buy_ff_231"),
            types.InlineKeyboardButton("🔙 العودة للألعاب", callback_data="games_menu")
        )
        bot.edit_message_text("🔥 **Free Fire**\nاختر الفئة المناسبة لشحن جواهر فري فاير:", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

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

    # بدء معالجة طلبات الشراء وتحديد اللعبة والكمية
    elif call.data.startswith("buy_pubg_") or call.data.startswith("buy_ff_"):
        game_type = "ببجي موبايل" if "pubg" in call.data else "فري فاير"
        unit = "UC" if "pubg" in call.data else "جوهرة"
        amount = call.data.split("_")[-1]
        
        user_orders[call.from_user.id] = {
            "game": game_type,
            "amount": f"{amount} {unit}",
            "step": "get_id"
        }
        
        bot.send_message(chat_id, f"🎮 الخاص بك في لعبة {game_type} الرجاء إدخال **الآيدي ID** الخاص بك:")
        bot.answer_callback_query(call.id)

    # معالجة ضغط الأدمن على زر جميع الطلبات
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

# --- معالجة الخطوات المتتالية (الآيدي ورقم المعاملة) ---
@bot.message_handler(func=lambda message: message.from_user.id in user_orders)
def process_order_steps(message):
    user_id = message.from_user.id
    step = user_orders[user_id]["step"]
    
    # الخطوة الأولى: استقبال الـ ID
    if step == "get_id":
        user_orders[user_id]["player_id"] = message.text
        user_orders[user_id]["step"] = "get_payment"
        
        payment_text = f"💰 **خطوة الدفع (الشام كاش):**\n\n" \
                       f"يرجى إرسال مبلغ الفئة المطلوبة إلى عنوان الشام كاش التالي:\n" \
                       f"📌 العنوان: `{SHAM_CASH_ACCOUNT}`\n\n" \
                       f"⚠️ بعد إتمام التحويل، أرسل رقم المعاملة أو الرقم المرجعي هنا لتأكيد طلبك:"
        bot.send_message(message.chat.id, payment_text, parse_mode="Markdown")
        
    # الخطوة الثانية والأخيرة: استقبال رقم المعاملة وإرسال الإشعارات وحفظ البيانات
    elif step == "get_payment":
        user_orders[user_id]["transaction_id"] = message.text
        order_info = user_orders[user_id]
        
        # 1. إرسال تأكيد مباشر للزبون بنجاح العملية
        success_text = f"✅ **تم استلام تفاصيل طلبك بنجاح!**\n\n" \
                       f"🎮 اللعبة: {order_info['game']}\n" \
                       f"📦 الفئة: {order_info['amount']}\n" \
                       f"🆔 معرف اللاعب (ID): `{order_info['player_id']}`\n" \
                       f"🧾 رقم معاملة التحويل: `{order_info['transaction_id']}`\n\n" \
                       f"⏳ جاري مراجعة عملية الدفع وشحن حسابك خلال دقائق معدودة. شكراً لثقتك بنا!"
        bot.send_message(message.chat.id, success_text, parse_mode="Markdown")
        
        # 2. تجهيز وإرسال الإشعار الفوري لك (للأدمن)
        username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
        admin_notification = f"🚨 **طلب شحن جديد وصلك الآن!**\n\n" \
                             f"👤 الحساب المستطرد للزبون: {username} (ID: {user_id})\n" \
                             f"🎮 اللعبة المطلوبة: {order_info['game']}\n" \
                             f"📦 الكمية/الفئة: {order_info['amount']}\n" \
                             f"🆔 آيدي اللاعب (ID): `{order_info['player_id']}`\n" \
                             f"🧾 الرقم المرجعي للمعاملة: `{order_info['transaction_id']}`"
                             
        try:
            bot.send_message(ADMIN_ID, admin_notification, parse_mode="Markdown")
        except Exception as e:
            print(f"حدث خطأ أثناء إرسال الرسالة لحساب الأدمن الرئيسي: {e}")
            
        # 3. حفظ الطلب في الملف النصي ليعمل مع زر "جميع الطلبات"
        save_order_to_file(admin_notification)
        
        # 4. تنظيف ذاكرة الطلبات الحالية للمستخدم لإتاحة طلب جديد لاحقاً
        del user_orders[user_id]

# --- تشغيل البوت المستمر ---
if __name__ == "__main__":
    print("🤖 البوت مبرمج وتعمل إشعاراته الآن بنجاح...")
    bot.infinity_polling()
