from db_functions import Database
from binance_functions import Binance
import telebot
import threading
import config
import requests
'''This is the complete Telegram bot. Trading functions are not included here'''

class Bot(object):
    def __init__(self):
        self.client = Binance(config.SPOTTEST_API_KEY, config.SPOTTEST_SECRET_KEY)
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

    def correct_user(self, message, db):
        ''' Check if correct user '''
        username = message.from_user.username
        user = db.user_check()
        if user == "None" and self.user_name_recorded == False:
            db.save_username()
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
            if self.correct_user(message, DB):
                chat_id = message.chat.id
                DB.save_chat_id()
                self.chat_id = chat_id
                bot.reply_to(message, "Hello " + message.from_user.first_name)

        @bot.message_handler(commands=['help'])
        def bot_info(message):
            DB = Database()
            if self.correct_user(message, DB):
                bot.reply_to(message, "Helloworld")

        @bot.message_handler(commands=['set'])
        def set_strategy(message):
            '''Sets a strategy for multiple orders: /set {side} {amount} {symbol} at {price}, then {side} {amount} {symbol} at {price}'''
            DB = Database()
            if self.correct_user(message, DB):
                bot.reply_to(message, "Helloworld")

        @bot.message_handler(commands=['order'])
        def set_strategy(message):
            '''Makes only one order: /order {type} {side} {amount} {symbol}'''
            DB = Database()
            if self.correct_user(message, DB):
                response = self.client.send_order(message)
                bot.reply_to(message, response)

        @bot.message_handler(commands=['ticker'])
        def current_price(message):
            DB = Database()
            if self.correct_user(message, DB):
                token = message.text.replace("/ticker", "").replace(" ", "").upper()
                link = self.ticker_link + token
                request = requests.get(link)
                data = request.json()
                bot.reply_to(message, data['symbol'] + ": " + data['price'])

        @bot.message_handler(commands=['strategy'])
        def show_strategy(message):
            DB = Database()
            if self.correct_user(message, DB):
                bot.reply_to(message, "Helloworld")

        @bot.message_handler(commands=['watch'])
        def show_strategy(message):
            '''Send alert when price of a token'''
            DB = Database()
            if self.correct_user(message, DB):
                bot.reply_to(message, "Helloworld")

        @bot.message_handler(commands=['cancelorder'])
        def cancel_order(message):
            DB = Database()
            if self.correct_user(message, DB):
                bot.reply_to(message, "Helloworld")

        @bot.message_handler(commands=['cancelwatch'])
        def cancel_order(message):
            '''Stops alert set by /watch'''
            DB = Database()
            if self.correct_user(message, DB):
                bot.reply_to(message, "Helloworld")

        @bot.message_handler(commands=['cancelstrategy'])
        def cancel_strategy(message):
            DB = Database()
            if self.correct_user(message, DB):
                bot.reply_to(message, "Helloworld")

        @bot.message_handler(commands=['account'])
        def show_account(message):
            DB = Database()
            if self.correct_user(message, DB):
                info = self.client.get_account()
                bot.reply_to(message, str(info))

        @bot.message_handler(commands=['orderbook'])
        def show_orderbook(message):
            DB = Database()
            if self.correct_user(message, DB):
                bot.reply_to(message, "Helloworld")
    # ----  ---- #

    # ---- Async Polling Setup ---- #
    def all_bot_actions(self):
        self.bot_commands(self.bot)
        self.bot.polling()

    def restart_async_polling(self):
        self.polling_thread = threading.Thread(target=self.all_bot_actions)
        self.polling_thread.start()

    def stop_async_polling(self):
        self.polling_thread.join()
        self.bot.stop_polling()
    # ---- ---- #
