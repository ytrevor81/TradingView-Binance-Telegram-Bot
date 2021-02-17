from db_functions import Database
import telebot
import threading
import config

'''This is the complete Telegram bot. Trading functions are not included here'''

class Bot(object):
    def __init__(self):
        self.bot = telebot.TeleBot(config.TELEGRAM_BOT_KEY)
        self.chat_id = None #will be assigned via message
        self.ticker_link = 'https://api.binance.com/api/v3/ticker/price?symbol=' #need to add symbol to the end

        self.polling_thread = threading.Thread(target=self.all_bot_actions)
        self.polling_thread.start()

    def initial_chat_id_check(self):
        ''' Default chat_id is 0 '''
        DB = Database()
        chat_id = DB.chat_id_check()
        if chat_id != 0:
            self.chat_id = chat_id

    def error_message(self, symbol, quantity, message_type):
        if message_type == "Denied":
            self.bot.send_message(self.chat_id, "A Binance order for " + str(quantity) + " " + symbol + " has been denied")
        else:
            self.bot.send_message(self.chat_id, "Error: " + message_type)

    def message(self, message):
        self.bot.send_message(self.chat_id, message)

    def bot_commands(self, bot):
        @bot.message_handler(commands=['start'])
        def initialize_bot(message):
            DB = Database()
            chat_id = message.chat.id
            DB.save_chat_id(chat_id)
            self.polling_thread.join()
            self.chat_id = chat_id
            bot.reply_to(message, "Chat Id saved")
            self.polling_thread = threading.Thread(target=self.all_bot_actions)
            self.polling_thread.start()

        @bot.message_handler(commands=['help'])
        def bot_info(message):
            #bot.reply_to(message, "Helloworld")
            bot.send_message(self.chat_id, "Helloworld")

        @bot.message_handler(commands=['set'])
        def set_strategy(message):
            bot.reply_to(message, "Helloworld")

        @bot.message_handler(commands=['ticker'])
        def current_price(message):
            bot.reply_to(message, "Helloworld")

        @bot.message_handler(commands=['strategy'])
        def show_strategy(message):
            bot.reply_to(message, "Helloworld")

        @bot.message_handler(commands=['cancel'])
        def cancel_strategy(message):
            bot.reply_to(message, "Helloworld")

    def all_bot_actions(self):
        self.bot_commands(self.bot)
        self.bot.polling()

    def async_polling(self):
        polling_thread = threading.Thread(target=self.all_bot_actions)
        #polling_thread.daemon = True
        polling_thread.start()
