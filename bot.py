from db_functions import Database
import telebot
import threading
import config
import requests
'''This is the complete Telegram bot. Trading functions are not included here'''

class Bot(object):
    def __init__(self):
        self.bot = telebot.TeleBot(config.TELEGRAM_BOT_KEY)
        self.chat_id = None #will be assigned via message
        self.user_name_recorded = False
        self.ticker_link = 'https://api.binance.com/api/v3/ticker/price?symbol=' #need to add symbol to the end

        # ---- Initializing Functions --- #
        self.initial_chat_id_check() #checks if chat_id is already in the DB
        self.polling_thread = threading.Thread(target=self.all_bot_actions) #The bot will be polling for messages asynchronously as the rest of the app runs
        self.polling_thread.start()

    def initial_chat_id_check(self):
        ''' Default chat_id is 0 '''
        DB = Database()
        chat_id = DB.chat_id_check()
        if chat_id != 0:
            self.chat_id = chat_id

    def correct_user(self, username, db):
        ''' Check if correct user '''
        user = db.user_check()
        if user == "None" and self.user_name_recorded == False:
            db.save_username(username)
            self.user_name_recorded = True
            return True
        elif user == username:
            return True
        else:
            return False

    def error_message(self, symbol, quantity, message_type):
        if message_type == "Denied":
            self.bot.send_message(self.chat_id, "A Binance order for " + str(quantity) + " " + symbol + " has been denied")
        else:
            self.bot.send_message(self.chat_id, "Error: " + message_type)

    def message(self, message):
        self.bot.send_message(self.chat_id, message)

    # ---- All Bot Commands are here ---- #
    def bot_commands(self, bot):
        @bot.message_handler(commands=['start'])
        def initialize_bot(message):
            DB = Database()
            chat_id = message.chat.id
            username = message.from_user.username
            if self.correct_user(username, DB):
                DB.save_chat_id(chat_id)
                self.chat_id = chat_id
                bot.send_message(self.chat_id, "Chat Id saved")

        @bot.message_handler(commands=['help'])
        def bot_info(message):
            DB = Database()
            chat_id = message.chat.id
            username = message.from_user.username
            if self.correct_user(username, DB):
                bot.send_message(self.chat_id, "Helloworld")

        @bot.message_handler(commands=['set'])
        def set_strategy(message):
            DB = Database()
            chat_id = message.chat.id
            username = message.from_user.username
            if self.correct_user(username, DB, "set"):
                bot.reply_to(message, "Helloworld")

        @bot.message_handler(commands=['ticker'])
        def current_price(message):
            DB = Database()
            chat_id = message.chat.id
            username = message.from_user.username
            if self.correct_user(username, DB):
                token = message.text.replace("/ticker", "").replace(" ", "").upper()
                link = self.ticker_link + token
                request = requests.get(link)
                data = request.json()
                bot.send_message(self.chat_id, data['symbol'] + ": " + data['price'])

        @bot.message_handler(commands=['strategy'])
        def show_strategy(message):
            DB = Database()
            chat_id = message.chat.id
            username = message.from_user.username
            if self.correct_user(username, DB):
                bot.reply_to(message, "Helloworld")

        @bot.message_handler(commands=['cancel'])
        def cancel_strategy(message):
            DB = Database()
            chat_id = message.chat.id
            username = message.from_user.username
            if self.correct_user(username, DB):
                bot.reply_to(message, "Helloworld")
    # ----  ---- #

    def all_bot_actions(self):
        self.bot_commands(self.bot)
        self.bot.polling()

    def restart_async_polling(self):
        self.polling_thread = threading.Thread(target=self.all_bot_actions)
        self.polling_thread.start()

    def stop_async_polling(self):
        self.polling_thread.join()
        self.bot.stop_polling()
