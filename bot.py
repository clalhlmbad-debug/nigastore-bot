import telebot
import requests
from telebot import types

T = "8826744317:AAGUEQRxn2aRnj9huWGzKlwYqXqzBZbMZP0"
K = "AatfAkAcp6XKyQKPYru8ZyaAZ6H0VkyNb4FXx1sgbV8hAtHEgw8Z0hQjNZNvcZs-"
U = "https://nemer-card.com"
A = 8192730669
S = "df910e178e027a6bfcae8b99b06b5384"

bot = telebot.TeleBot(T)
user_status = {}
user_data = {}

def fetch_products_from_api(exact_server_name):
    h = {"Authorization": f"Bearer {K}"}
    try:
        r = requests.get(f"{U}/api/products", headers=h, timeout=10)
        if r.status_code == 200:
            all_p = r.json().get("data", [])
            f_list = []
            for p in all_p:
                n = p.get("name", "").lower()
                c = p.get("category", "").lower()
                if exact_server_name.lower() in n or exact_server_name.lower() in c:
                    f_list.append(p)
            return f_list
    except Exception as e:
        print(f"API Error")
    return []

def main_menu_markup():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton(text="🎮 Games Section", callback_data="g_m"),
        types.InlineKeyboardButton(text="📱 Apps Section", callback_data="ap_1"),
        types.InlineKeyboardButton(text="💳 Digital Cards", callback_data="c_m"),
        types.InlineKeyboardButton(text="💰 Balance Charge", callback_data="ch_m")
    )
    return m

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Welcome to Niga Store bot! Choose service:", reply_markup=main_menu_markup())

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    
    if call.data == "main_menu":
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Choose service:", reply_markup=main_menu_markup())

    elif call.data == "g_m":
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton(text="🔫 PUBG S1", callback_data="get_api_ببجي موبايل S1"),
            types.InlineKeyboardButton(text="🔥 Free Fire S1", callback_data="get_api_فري فاير S1"),
            types.InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")
        )
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Choose game:", reply_markup=m)

    elif call.data == "ap_1":
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(
            types.InlineKeyboardButton(text="🎙️ Bigo", callback_data="get_api_Bigo Live"),
            types.InlineKeyboardButton(text="💬 Tami", callback_data="get_api_TAMI CHAT"),
            types.InlineKeyboardButton(text="💬 Light", callback_data="get_api_LIGHT CHAT"),
            types.InlineKeyboardButton(text="🦊 Junko", callback_data="get_api_JUNKO CHAT"),
            types.InlineKeyboardButton(text="🔵 Ligo", callback_data="get_api_LIGO LIVE"),
            types.InlineKeyboardButton(text="🎵 Soul", callback_data="get_api_SOUL STAR")
        )
        m.row(types.InlineKeyboardButton(text="➡️ Next", callback_data="ap_2"))
        m.row(types.InlineKeyboardButton(text="🔙 Back", callback_data="main_menu"))
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Apps Page 1:", reply_markup=m)

    elif call.data == "ap_2":
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(
            types.InlineKeyboardButton(text="🟡 YoYo", callback_data="get_api_YOYO CHAT"),
            types.InlineKeyboardButton(text="🦁 Haki", callback_data="get_api_HAKI CHAT"),
            types.InlineKeyboardButton(text="💟 Hiya", callback_data="get_api_HIYA CHAT"),
            types.InlineKeyboardButton(text="👁️ 4Fun", callback_data="get_api_4FUN CHAT"),
            types.InlineKeyboardButton(text="🌸 Lami", callback_data="get_api_LAMI CHAT"),
            types.InlineKeyboardButton(text="🦖 YoHo", callback_data="get_api_YOHO WAKA")
        )
        m.row(types.InlineKeyboardButton(text="⬅️ Prev", callback_data="ap_1"))
        m.row(types.InlineKeyboardButton(text="🔙 Back", callback_data="main_menu"))
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Apps Page 2:", reply_markup=m)

    elif call.data == "c_m":
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton(text="🍏 iTunes", callback_data="get_api_آيتونز"),
            types.InlineKeyboardButton(text="🤖 Google Play", callback_data="get_api_جوجل"),
            types.InlineKeyboardButton(text="🟢 Razer Gold", callback_data="get_api_رايزر"),
            types.InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")
        )
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Choose card type:", reply_markup=m)

    elif call.data.startswith("get_api_"):
        ik = call.data.replace("get_api_", "")
        bot.send_message(chat_id, f"Connecting to server for {ik}...")
        products = fetch_products_from_api(ik)
        if products:
            m = types.InlineKeyboardMarkup(row_width=1)
            for prod in products:
                bt = f"{prod['name']} - Price: {prod['price']}$"
                m.add(types.InlineKeyboardButton(text=bt, callback_data=f"buy_{prod['name']}"))
            m.add(types.InlineKeyboardButton(text="🔙 Back", callback_data="main_menu"))
            bot.send_message(chat_id, f"Available items for {ik}:", reply_markup=m)
        else:
            bot.send_message(chat_id, f"No packages found for {ik} in your dashboard.")

    elif call.data.startswith("buy_"):
        pn = call.data.replace("buy_", "")
        user_data[chat_id] = {"item": pn}
        user_status[chat_id] = "w_p"
        bot.send_message(chat_id, f"Selected: {pn}\n\nPlease enter Player ID:")

    elif call.data == "ch_m":
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton(text="💵 Sham Cash", callback_data="p_s"),
            types.InlineKeyboardButton(text="🪙 USDT (TRC20)", callback_data="p_u"),
            types.InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")
        )
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Choose deposit method:", reply_markup=m)

    elif call.data == "p_s":
        user_status[chat_id] = "w_s_a"
        bot.send_message(chat_id, "Enter transferred amount (Numbers only):")

    elif call.data == "p_u":
        user_status[chat_id] = "w_p_u"
        bot.send_message(chat_id, "Send USDT to TRC20 address:\n`TYxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`\n\nThen send receipt screenshot:")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text_inputs(message):
    chat_id = message.chat.id
    st = user_status.get(chat_id)
    if st == "w_s_a":
        user_data[chat_id] = {"amount": message.text}
        user_status[chat_id] = "w_p_s"
        bot.reply_to(message, "Send receipt screenshot:")
    elif st == "w_p":
        player_id = message.text
        item_name = user_data.get(chat_id, {}).get("item", "product")
        bot.reply_to(message, "Order submitted! Admin will process it soon.")
        admin_text = f"🛒 New Order!\n\nUser: @{message.from_user.username or 'No User'}\nUser ID: `{chat_id}`\nItem: {item_name}\nTarget ID: `{player_id}`"
        bot.send_message(A, admin_text)
        user_status[chat_id] = None

@bot.message_handler(content_types=['photo'])
def handle_payment_proof(message):
    chat_id = message.chat.id
    st = user_status.get(chat_id)
    if chat_id in user_status and st in ["w_p_s", "w_p_u"]:
        if st == "w_p_s":
            amount = user_data.get(chat_id, {}).get("amount", "unknown")
            bot.reply_to(message, "Receipt received! Admin will check and add balance.")
            admin_text = f"🚨 New Sham Cash Deposit!\n\nMerchant: `{S}`\nUser: @{message.from_user.username or 'No User'}\nUser ID: `{chat_id}`\nAmount: {amount} SYP"
            bot.send_photo(A, message.photo[-1].file_id, caption=admin_text)
        elif st == "w_p_u":
            bot.reply_to(message, "USDT receipt received. Admin will check.")
            admin_text = f"🚨 New USDT Deposit!\n\nUser: @{message.from_user.username or 'No User'}\nUser ID: `{chat_id}`"
            bot.send_photo(A, message.photo[-1].file_id, caption=admin_text)
        user_status[chat_id] = None
    else:
        bot.reply_to(message, "Please use the buttons first.")

print("Bot is running successfully...")
bot.infinity_polling()
