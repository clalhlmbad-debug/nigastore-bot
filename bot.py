import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8826744317:AAEhuJxpjx8m9i17rwvEJmca75qrJOvJ55M"
bot = telebot.TeleBot(TOKEN)

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
            InlineKeyboardButton("🔫 ببجي", callback_data="pubg_info"),
            InlineKeyboardButton("🔥 فري فاير", callback_data="ff_info"),
            InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu")
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🎮 مرحباً بك في قسم الألعاب! اختر لعبتك المفضلة:", reply_markup=markup)
    elif call.data == "pubg_info":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 عودة لقسم الألعاب", callback_data="games_menu"))
        pubg_text = "🎯 **قسم ببجي موبايل (PUBG Mobile)**\n\n• شحن شدات ببجي (UC)\n• مسابقات وفعاليات روم يومية\n• حسابات للبيع\n\n💡 للطلب والاستفسار تواصل مع الدعم الفني."
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=pubg_text, parse_mode="Markdown", reply_markup=markup)
    elif call.data == "ff_info":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 عودة لقسم الألعاب", callback_data="games_menu"))
        ff_text = "🔥 **قسم فري فاير (Free Fire)**\n\n• شحن جواهر فري فاير (Diamonds)\n• أكواد استبدال الهدايا\n\n💡 للطلب والاستفسار تواصل مع الدعم الفني."
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=ff_text, parse_mode="Markdown", reply_markup=markup)
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

print("البوت يعمل الآن بنجاح...")
bot.infinity_polling()
