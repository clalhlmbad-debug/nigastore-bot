import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# --- إعدادات سيرفر وهمي للحفاظ على مجانية الـ Render ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Live and Running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعدادات البوت الأساسية (قم بتعديلها) ---
# ⚠️ ضع توكن البوت الخاص بك المستخرج من BotFather بين الفواصل
BOT_TOKEN = "8826744317:AAEY8S9xK4B4dXA3-kN2J6JyBF3ng701Ipg" 

# ⚠️ ضع الآيدي (ID) المكون من أرقام لحسابك الشخصي لكي تصلك طلبات الشحن والإيصالات عليه
ADMIN_ID = 8192730669 # استبدل هذا الرقم بآيدي حسابك الحقيقي

# عنوان محفظة شام كاش الخاصة بك التي زودتني بها
SHAM_CASH_WALLET = "df910e178e027a6bfcae8b99b06b5384"

bot = telebot.TeleBot(BOT_TOKEN)

# تخزين مؤقت لحالات المستخدمين والطلبات
user_data = {}
orders = {}

# قائمة الباقات والأسعار (يمكنك تعديل الأسعار والكميات من هنا بسهولة)
PRICES = {
    'pubg': {
        'b1': {'name': '60 شدة (UC)', 'price': '15,000 ل.س'},
        'b2': {'name': '325 شدة (UC)', 'price': '65,000 ل.س'},
        'b3': {'name': '660 شدة (UC)', 'price': '125,000 ل.س'}
    },
    'freefire': {
        'f1': {'name': '100 جوهرة', 'price': '12,000 ل.س'},
        'f2': {'name': '210 جوهرة', 'price': '24,000 ل.س'},
        'f3': {'name': '530 جوهرة', 'price': '55,000 ل.س'}
    }
}

# أمر البداية /start
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.chat.id
    user_data[user_id] = {}
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_pubg = types.InlineKeyboardButton("🎮 شحن ببجي (PUBG UC)", callback_data="game_pubg")
    btn_ff = types.InlineKeyboardButton("💎 فري فاير (Free Fire)", callback_data="game_freefire")
    markup.add(btn_pubg, btn_ff)
    
    welcome_text = "👋 أهلاً بك في بوت شحن الألعاب المعتمد!\n\nيرجى اختيار اللعبة التي ترغب في شحنها من الأزرار أدناه:"
    bot.send_message(user_id, welcome_text, reply_markup=markup)

# معالجة الضغط على الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.message.chat.id
    
    # اختيار اللعبة
    if call.data.startswith("game_"):
        game = call.data.split("_")[1]
        user_data[user_id]['game'] = game
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, package in PRICES[game].items():
            btn = types.InlineKeyboardButton(f"{package['name']} - بسعر {package['price']}", callback_data=f"pkg_{key}")
            markup.add(btn)
        
        btn_back = types.InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data="main_menu")
        markup.add(btn_back)
        
        bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, 
                              text="📦 يرجى اختيار الباقة المناسبة لك:", reply_markup=markup)
        
    # العودة للقائمة الرئيسية
    elif call.data == "main_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_pubg = types.InlineKeyboardButton("🎮 شحن ببجي (PUBG UC)", callback_data="game_pubg")
        btn_ff = types.InlineKeyboardButton("💎 فري فاير (Free Fire)", callback_data="game_freefire")
        markup.add(btn_pubg, btn_ff)
        bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, 
                              text="يرجى اختيار اللعبة التي ترغب في شحنها من الأزرار أدناه:", reply_markup=markup)

    # اختيار الباقة
    elif call.data.startswith("pkg_"):
        pkg_key = call.data.split("_")[1]
        game = user_data[user_id].get('game')
        
        if not game:
            bot.send_message(user_id, "⚠️ حدوث خطأ، يرجى إعادة تشغيل البوت عبر أمر /start")
            return
            
        user_data[user_id]['package'] = PRICES[game][pkg_key]['name']
        user_data[user_id]['price'] = PRICES[game][pkg_key]['price']
        
        # الانتقال لطلب المعرف ID
        msg = bot.send_message(user_id, "🆔 من فضلك، قم بكتابة معرف اللاعب الخاص بك (Player ID) في اللعبة:")
        bot.register_next_step_handler(msg, get_player_id)

    # لوحة تحكم الإدارة (قبول / رفض الطلب)
    elif call.data.startswith("admin_"):
        action, order_id = call.data.split("_")[1], call.data.split("_")[2]
        order = orders.get(order_id)
        
        if order:
            customer_id = order['user_id']
            if action == "approve":
                bot.send_message(customer_id, f"✅ **تهانينا!** تم تأكيد دفعتك بنجاح وشحن باقة **({order['package']})** لحسابك بنجاح. شكراً لثقتك بنا!")
                bot.edit_message_text(chat_id=ADMIN_ID, message_id=call.message.message_id, 
                                      text=f"🟢 تم [قبول وشحن] طلب العميل بنجاح.\nاللاعب: {order['player_id']}")
            elif action == "reject":
                bot.send_message(customer_id, "❌ **نعتذر منك!** تم رفض طلب الشحن الخاص بك نظراً لعدم صحة بيانات التحويل أو نقصها. يرجى التواصل مع الدعم الفني.")
                bot.edit_message_text(chat_id=ADMIN_ID, message_id=call.message.message_id, 
                                      text=f"🔴 تم [رفض] طلب العميل.\nاللاعب: {order['player_id']}")
            # تنظيف الذاكرة للطلب المستهلك
            orders.pop(order_id, None)

# استلام رقم الآيدي والاسم
def get_player_id(message):
    user_id = message.chat.id
    player_id = message.text
    user_data[user_id]['player_id'] = player_id
    
    # رسالة الدفع عبر شام كاش
    payment_text = (
        f"💳 **تفاصيل الدفع الفوري:**\n\n"
        f"الرجاء تحويل مبلغ **{user_data[user_id]['price']}** إلى حسابنا في **شام كاش** التالي:\n\n"
        f"`{SHAM_CASH_WALLET}`\n\n"
        f"💡 *(اضغط على العنوان أعلاه لنسخه تلقائياً)*\n\n"
        f"📸 بعد إتمام عملية التحويل بنجاح، يرجى إرسال **صورة إيصال التحويل** أو لقطة شاشة للعملية هنا في الشات لإتمام الشحن الفوري مجاناً:"
    )
    msg = bot.send_message(user_id, payment_text, parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_payment_proof)

# استلام إيصال التحويل وإرساله للأدمن
def get_payment_proof(message):
    user_id = message.chat.id
    
    # التأكد من إرسال صورة أو نص كإيصال
    if message.content_type in ['photo', 'text']:
        order_id = str(user_id) + "_" + str(message.message_id)
        
        orders[order_id] = {
            'user_id': user_id,
            'game': user_data[user_id].get('game'),
            'package': user_data[user_id].get('package'),
            'price': user_data[user_id].get('price'),
            'player_id': user_data[user_id].get('player_id')
        }
        
        # إنشاء أزرار التحكم للأدمن
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        btn_app = types.InlineKeyboardButton("✅ قبول وشحن", callback_data=f"admin_approve_{order_id}")
        btn_rej = types.InlineKeyboardButton("❌ رفض الطلب", callback_data=f"admin_reject_{order_id}")
        admin_markup.add(btn_app, btn_rej)
        
        admin_info = (
            f"🔔 **طلب شحن جديد وارد!**\n\n"
            f"🎮 اللعبة: {orders[order_id]['game'].upper()}\n"
            f"📦 الباقة: {orders[order_id]['package']}\n"
            f"💰 السعر المطلوب: {orders[order_id]['price']}\n"
            f"🆔 آيدي اللاعب (ID): `{orders[order_id]['player_id']}`\n"
            f"👤 حساب المشتري: {message.from_user.first_name} (@{message.from_user.username})"
        )
        
        # إرسال البيانات للأدمن مع الإيصال ليتأكد يدوياً
        if message.content_type == 'photo':
            photo_id = message.photo[-1].file_id
            bot.send_photo(ADMIN_ID, photo_id, caption=admin_info, parse_mode="Markdown", reply_markup=admin_markup)
        else:
            admin_info += f"\n\n📝 رقم العملية المرسل: {message.text}"
            bot.send_message(ADMIN_ID, admin_info, parse_mode="Markdown", reply_markup=admin_markup)
            
        bot.send_message(user_id, "⏳ **تم استلام طلبك بنجاح وجاري مراجعته من قبل الإدارة.**\nسيصلك إشعار فوري هنا عند تأكيد عملية الشحن!")
    else:
        msg = bot.send_message(user_id, "⚠️ يرجى إرسال صورة إيصال صحيحة أو لقطة شاشة للعملية:")
        bot.register_next_step_handler(msg, get_payment_proof)

# تشغيل السيرفر والبوت
if __name__ == '__main__':
    keep_alive() # تشغيل الفلاسك لـ Render
    print("Bot is starting...")
    bot.infinity_polling()
