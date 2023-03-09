
import telegram
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
# from telegram.constants import ParseMode

from server.settings.secrects import TELEGRAM_BOT_TOKEN,TELEGRAM_WEBHOOK_URL,TELEGRAM_ADMIN_CHAT_ID
bot_instance = None
def init_bot():
    
    global bot_instance
    try:
        bot_instance = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        bot_instance.set_webhook(TELEGRAM_WEBHOOK_URL)
        print('bot_instance: ', bot_instance)
        
    except Exception as e:
        print(e)
        bot_instance = None
        pass
    
def get_bot():
    return bot_instance


def edit_message_reply_markup(message_id, chat_id=TELEGRAM_ADMIN_CHAT_ID, reply_markup=None):
    bot_instance.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)

def send_admin_message(message:str,parse_mode=ParseMode.HTML,reply_markup=None, reply_to_message_id=None, asset=None, asset_type=None):
    bot = get_bot()
    if bot:
        if asset:
            if asset_type == 'image':
                bot.send_photo(chat_id=TELEGRAM_ADMIN_CHAT_ID, photo=asset, caption=message,reply_markup=reply_markup,reply_to_message_id=reply_to_message_id,parse_mode=parse_mode)
            elif asset_type == 'video':
                bot.send_video(chat_id=TELEGRAM_ADMIN_CHAT_ID, video=asset, caption=message,reply_markup=reply_markup,reply_to_message_id=reply_to_message_id,parse_mode=parse_mode)
        else:
            bot.send_message(chat_id=TELEGRAM_ADMIN_CHAT_ID, text=message,reply_markup=reply_markup,reply_to_message_id=reply_to_message_id,parse_mode=parse_mode)
    else:
        print('bot not initialized')