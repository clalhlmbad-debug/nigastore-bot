import telebot
from telebot import types
import os
import sqlite3
from flask import Flask
from threading import Thread

# --- إعدادات سيرفر الحفاظ على مجانية الـ Render ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Live and Running with SQLite Photo DB!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعدادات البوت الأساسية المتكاملة ---
BOT_TOKEN = '8826744317:AAEY8S9xK4B4dXA3-kN2J6JyBF3ng701Ipg'
ADMIN_ID = 8192730669
SHAM_CASH_WALLET = "df910e178e027a6bfcae8b99b06b5384"

bot = telebot.TeleBot(BOT_TOKEN)

# تخزين مؤقت لجلسات المستخدمين الحالية (أثناء التصفح)
user_sessions = {}

# --- إعداد وإنشاء قاعدة البيانات لحفظ الطلبات بصورها ---
def init_db():
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            user_id INTEGER,
            package_name TEXT,
            player_id TEXT,
            photo_id TEXT,
            status TEXT DEFAULT 'PENDING'
        )
    ''')
    conn.commit()
    conn.close()

# تشغيل دالة إنشاء قاعدة البيانات فوراً
init_db()

# قائمة الباقات الاحترافية المنسقة
PACKAGES = {
    'pubg_b1': {'game': '🎮 ببجي موبايل', 'name': '60 شدة (UC)', 'price': '15,000 ل.س'},
    'pubg_b2': {'game': '🎮 ببجي موبايل', 'name': '325 شدة (UC)', 'price': '65,000 ل.س'},
    'pubg_b3': {'game': '🎮 ببجي موبايل', 'name': '660 شدة (UC)', 'price': '125,000 ل.س'},
    'ff_f1': {'game': '💎 فري فاير', 'name': '100 جوهرة', 'price': '12,000 ل.س'},
    'ff_f2': {'game': '💎 فري فاير', 'name': '210 جوهرة', 'price': '24,000 ل.س'},
    'ff_f3': {'game': '💎 فري فاير', 'name': '530 جوهرة', 'price': '55,000 ل.س'}
}

# رسالة الترحيب الرئيسية /start
@bot.message_handler(commands=['start'])
def start_message(message):
    uid = message.chat.id
    user_sessions[uid] = {} 
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_pubg = types.InlineKeyboardButton("🎮 شحن شدات ببجي (PUBG UC)", callback_data="show_pubg")
    btn_ff = types.InlineKeyboardButton("🔥 شحن جواهر فري فاير (Free Fire)", callback_data="show_freefire")
    markup.add(btn_pubg, btn_ff)
    
    welcome_text = (
        "⚡ **أهلاً بك في متجر شحن الألعاب الفوري المعتمد!** ⚡\n\n"
        "تقدم لك منصتنا أسرع خدمة شحن شدات وجواهر بأسعار منافسة وطرق دفع آمنة.\n\n"
        "👇 **من فضلك اختر اللعبة التي ترغب في شحنها الآن:**"
    )
    bot.send_message(uid, welcome_text, parse_mode="Markdown", reply_markup=markup)

# معالجة ضغطات الأزرار واختيار الباقات
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.message.chat.id
    
    # عرض باقات ببجي
    if call.data == "show_pubg":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, pkg in PACKAGES.items():
            if key.startswith('pubg_'):
                markup.add(types.InlineKeyboardButton(f"📦 {pkg['name']} ← السعر: {pkg['price']}", callback_data=f"select_{key}"))
        markup.add(types.InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data="go_home"))
        
        bot.edit_message_text(chat_id=uid, message_id=call.message.message_id, 
                              text="🛒 **باقات شدات ببجي موبايل المتوفرة حالياً:**\nاختر الباقة المناسبة لبدء الشحن:", parse_mode="Markdown", reply_markup=markup)
        
    # عرض باقات فري فاير
    elif call.data == "show_freefire":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, pkg in PACKAGES.items():
            if key.startswith('ff_'):
                markup.add(types.InlineKeyboardButton(f"📦 {pkg['name']} ← السعر: {pkg['price']}", callback_data=f"select_{key}"))
        markup.add(types.InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data="go_home"))
        
        bot.edit_message_text(chat_id=uid, message_id=call.message.message_id, 
                              text="🛒 **باقات جواهر فري فاير المتوفرة حالياً:**\nاختر الباقة المناسبة لبدء الشحن:", parse_mode="Markdown", reply_markup=markup)

    # العودة للقائمة الرئيسية
    elif call.data == "go_home":
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_pubg = types.InlineKeyboardButton("🎮 شحن شدات ببجي (PUBG UC)", callback_data="show_pubg")
        btn_ff = types.InlineKeyboardButton("🔥 شحن جواهر فري فاير (Free Fire)", callback_data="show_freefire")
        markup.add(btn_pubg, btn_ff)
        bot.edit_message_text(chat_id=uid, message_id=call.message.message_id, 
                              text="⚡ **من فضلك اختر اللعبة التي ترغب في شحنها الآن:**", parse_mode="Markdown", reply_markup=markup)

    # اختيار باقة محددة والانتقال لطلب الـ ID
    elif call.data.startswith("select_"):
        pkg_id = call.data.replace("select_", "")
        user_sessions[uid] = {'package_key': pkg_id}
        
        msg = bot.send_message(uid, "🆔 **من فضلك، قم بكتابة معرف اللاعب الخاص بك (Player ID) بدقة في اللعبة:**")
        bot.register_next_step_handler(msg, process_player_id)

    # لوحة تحكم الإدارة للأدمن (تم إصلاح الخطأ البرمجي هنا)
    elif call.data.startswith("adm_"):
        parts = call.data.split("_")
        action = parts[1]
        order_id = parts[2] + "_" + parts[3]
        
        # جلب بيانات الطلب من قاعدة البيانات لتفادي التكرار
        conn = sqlite3.connect('orders.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, package_name, player_id, status FROM orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        
        if row:
            customer_id, package_name, player_id, current_status = row
            
            if current_status == 'PENDING':
                if action == "approve":
                    cursor.execute("UPDATE orders SET status = 'APPROVED' WHERE order_id = ?", (order_id,))
                    conn.commit()
                    
                    success_txt = f"🎉 **تهانينا!** تم تأكيد عملية الدفع وشحن باقة **({package_name})** لحساب الـ ID الخاص بك: `{player_id}` بنجاح.\n\nشكراً لتعاملك معنا وتمنياتنا لك بلعب ممتع! 🎮✨"
                    bot.send_message(customer_id, success_txt, parse_mode="Markdown")
                    bot.edit_message_text(chat_id=ADMIN_ID, message_id=call.message.message_id, 
                                          text=f"🟢 **تم تسليم وشحن طلب اللاعب:** `{player_id}` بنجاح.")
                elif action == "reject":
                    cursor.execute("UPDATE orders SET status = 'REJECTED' WHERE order_id = ?", (order_id,))
                    conn.commit()
                    
                    fail_txt = "❌ **نعتذر منك!** تم رفض طلب الشحن الخاص بك نظراً لعدم صحة بيانات التحويل أو لعدم وضوح الإيصال المرفق. يرجى مراجعة الدعم وإعادة المحاولة."
                    bot.send_message(customer_id, fail_txt, parse_mode="Markdown")
                    bot.edit_message_text(chat_id=ADMIN_ID, message_id=call.message.message_id, 
                                          text=f"🔴 **تم رفض طلب اللاعب:** `{player_id}`.")
            else:
                bot.answer_callback_query(call.id, "⚠️ تم اتخاذ إجراء سابق على هذا الطلب بالفعل!")
        else:
            bot.answer_callback_query(call.id, "⚠️ لم يتم العثور على هذا الطلب!")
        conn.close()

# الخطوة الثانية: استلام الـ ID وطلب الدفع عبر شام كاش ورفع الإيصال
def process_player_id(message):
    uid = message.chat.id
    player_id = message.text
    
    if uid not in user_sessions or 'package_key' not in user_sessions[uid]:
        bot.send_message(uid, "⚠️ عذراً، حدث خطأ في الجلسة. يرجى البدء من جديد عبر إرسال /start")
        return
        
    user_sessions[uid]['player_id'] = player_id
    pkg = PACKAGES[user_sessions[uid]['package_key']]
    
    payment_instruction = (
        f"💳 **خطوة الدفع الفوري (شام كاش):**\n\n"
        f"لإتمام شحن باقة **{pkg['name']}** للعبة **{pkg['game']}**:\n"
        f"💵 يرجى تحويل مبلغ قيمته: **{pkg['price']}** إلى عنوان المحفظة التالي:\n\n"
        f"`{SHAM_CASH_WALLET}`\n\n"
        f"💡 *(ملاحظة: يمكنك الضغط على عنوان المحفظة أعلاه لنسخه تلقائياً بنقرة واحدة)*\n\n"
        f"📸 بعد إتمام التحويل بنجاح، **قم بالتقاط لقطة شاشة لإيصال التحويل وإرسال الصورة هنا مباشرة** لتأكيد طلبك فورا:"
    )
    msg = bot.send_message(uid, payment_instruction, parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_payment_photo)

# الخطوة الأخيرة: استلام صورة الإيصال، حفظها في قاعدة البيانات وإرسالها للأدمن
def process_payment_photo(message):
    uid = message.chat.id
    
    # التأكد أن المستخدم أرسل صورة بالفعل
    if message.content_type != 'photo':
        msg = bot.send_message(uid, "⚠️ يرجى إرسال صورة إيصال الدفع (لقطة الشاشة) بشكل صحيح لتوثيق تحويلك:")
        bot.register_next_step_handler(msg, process_payment_photo)
        return

    if uid not in user_sessions or 'package_key' not in user_sessions[uid] or 'player_id' not in user_sessions[uid]:
        bot.send_message(uid, "⚠️ عذراً، انتهت الجلسة لطول الانتظار، يرجى إعادة البدء عبر /start")
        return

    pkg = PACKAGES[user_sessions[uid]['package_key']]
    player_id = user_sessions[uid]['player_id']
    photo_id = message.photo[-1].file_id # جلب أفضل جودة للصورة المرسلة
    
    order_id = f"{uid}_{message.message_id}"
    
    # حفظ الطلب بالإيصال والصورة داخل قاعدة البيانات SQLite بشكل دائم
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO orders (order_id, user_id, package_name, player_id, photo_id) VALUES (?, ?, ?, ?, ?)",
                   (order_id, uid, pkg['name'], player_id, photo_id))
    conn.commit()
    conn.close()
    
    # أزرار تحكم الأدمن
    admin_markup = types.InlineKeyboardMarkup(row_width=2)
    btn_approve = types.InlineKeyboardButton("✅ قبول وشحن", callback_data=f"adm_approve_{order_id}")
