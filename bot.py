from db_functions import Database
from binance_functions import Binance
import telebot, threading, config, requests, csv, os, time
from message_filter_functions import *
'''This is the complete Telegram bot. Trading functions are not included here'''

class Bot(object):
    def __init__(self):
        self.client = Binance(config.SPOTTEST_API_KEY, config.SPOTTEST_SECRET_KEY)
        self.bot = telebot.TeleBot(config.TELEGRAM_BOT_KEY)
        self.chat_id = None #will be assigned via message
        self.user_name_recorded = False
        self.ticker_link = 'https://api.binance.com/api/v3/ticker/price?symbol=' #need to add symbol to the end
        self.general_error_message = "Incorrect syntax or symbol. Please see example below or see /help \n\n" # Add onto the end of this message the specific command syntax needed
        self.csv_file_name = None #this will automatically delete any csv file called on /orderhistory
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

        @bot.message_handler(commands=['market'])
        def make_market_order(message):
            '''Market order: /market {side} {amount} {symbol}'''
            DB = Database()
            if self.correct_user(message, DB):
                try:
                    order_confirmation = self.client.send_order("market", message)
                    bot.reply_to(message, order_confirmation)
                except Exception as e:
                    print(str(e))
                    bot.reply_to(message, self.general_error_message + "ex. /market buy 0.01 eth \n(/market {side} {amount} {symbol})")

        @bot.message_handler(commands=['limit'])
        def make_limit_order(message):
            '''Limit order: /limit {timeInForce} {side} {amount} {symbol} at {price}'''
            DB = Database()
            if self.correct_user(message, DB):
                try:
                    order_confirmation = self.client.send_order("limit", message)
                    bot.reply_to(message, order_confirmation)
                except Exception as e:
                    print(str(e))
                    bot.reply_to(message, self.general_error_message + "ex. /limit gtc sell 0.01 ethusdt at 1858 \n(/limit {timeInForce} {side} {amount} {symbol} at {price})")

        @bot.message_handler(commands=['stoploss'])
        def make_stoploss_order(message):
            '''Makes only one order: /stoploss {timeInForce} {side} {amount} {symbol} at {price} stop at {stopLoss}'''
            DB = Database()
            if self.correct_user(message, DB):
                try:
                    order_confirmation = self.client.send_order("stoploss", message)
                    bot.reply_to(message, order_confirmation)
                except Exception as e:
                    print(str(e))
                    bot.reply_to(message, self.general_error_message + "ex. /stoploss gtc sell 0.1 btc at 55000 stop at 56000\n (/stoploss {timeInForce} {side} {amount} {symbol} at {price} stop at {stopLoss})")

        @bot.message_handler(commands=['ticker'])
        def current_price(message):
            ''' Checks current price of a token '''
            DB = Database()
            if self.correct_user(message, DB):
                try:
                    quick_token_text = message.text.replace("/ticker", "").replace(" ", "").upper()
                    if "USDT" in quick_token_text:
                        token = quick_token_text
                    else:
                        token = quick_token_text + "USDT"
                    link = self.ticker_link + token
                    request = requests.get(link)
                    data = request.json()
                    bot.reply_to(message, data['symbol'] + ": " + data['price'])
                except Exception as e:
                    bot.reply_to(message, self.general_error_message + "ex. /ticker btc or /ticker btcusdt")

        @bot.message_handler(commands=['watch'])
        def show_strategy(message):
            '''Send alert when price of a token'''
            DB = Database()
            if self.correct_user(message, DB):
                bot.reply_to(0, "Helloworld")

        @bot.message_handler(commands=['orderhistory'])
        def show_order_history(message):
            ''' View order history: /orderhistory
            Sends a csv of their past orders'''
            DB = Database()
            if self.correct_user(message, DB):
                try:
                    if self.csv_file_name != None:
                        os.remove(self.csv_file_name) #Deletes file once sent
                        self.csv_file_name = None
                    quick_token_text = message.text.replace("/orderhistory", "").replace(" ", "").upper()
                    if "USDT" in quick_token_text:
                        token = quick_token_text
                    else:
                        token = quick_token_text + "USDT"
                    all_orders = self.client.see_all_orders(token)
                    self.order_history_csv(token, all_orders)
                    doc = open(self.csv_file_name, 'rb')
                    bot.send_document(self.chat_id, doc)
                except Exception as e:
                    print(str(e))
                    bot.reply_to(message, self.general_error_message + "ex. /orderhistory btc \n\n/orderhistory {symbol}\n\nAlso make sure that you have made orders in the past using the token in question")

        @bot.message_handler(commands=['openorders'])
        def show_open_orders(message):
            ''' View order history: /openorders {symbol}'''
            DB = Database()
            if self.correct_user(message, DB):
                try:
                    quick_token_text = message.text.replace("/openorders", "").replace(" ", "").upper()
                    if "USDT" in quick_token_text:
                        token = quick_token_text
                    else:
                        token = quick_token_text + "USDT"
                    open_orders = self.client.open_orders(token)
                    self.open_orders_message_chain(open_orders, bot, token)
                except Exception as e:
                    print(str(e))
                    bot.reply_to(message, self.general_error_message + "ex. /openorders eth\n\n/openorders {symbol}\n\nAlso make sure that you have made orders in the past using the token in question")

        @bot.message_handler(commands=['cancel'])
        def cancel_order(message):
            '''Cancels an order /cancel {symbol} {orderId}'''
            DB = Database()
            if self.correct_user(message, DB):
                try:
                    cancelled_order = self.client.cancel_order(message)
                    cancel_message = cancelled_message(cancelled_order)
                    bot.reply_to(message, cancel_message)
                except Exception as e:
                    print(str(e))
                    bot.reply_to(message, self.general_error_message + "ex. /cancel eth 6963\n\n/cancel {symbol} {order Id}\n\n")

        @bot.message_handler(commands=['account'])
        def show_account(message):
            DB = Database()
            if self.correct_user(message, DB):
                info = self.client.get_account()
                bot.reply_to(message, str(info))

    # ----  ---- #

    # ---- Order History CSV ---- #
    def order_history_csv(self, token, order_history):
        filename = token + "_Order_History.csv"
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Order ID',
                             'Client Order ID',
                             'Price',
                             'Original Quantity',
                             'Executed Quantity',
                             'Cummulative Quote Quantity',
                             'Status',
                             'Time In Force',
                             'Type',
                             'Side',
                             'Stop Price',
                             'Iceberg Quantity',
                             'Original Quote Order Quantity'])
        with open(filename, 'a') as f:
            writer = csv.writer(f)
            for order in order_history:
                writer.writerow([order['orderId'],
                                 order['clientOrderId'],
                                 order['price'],
                                 order['origQty'],
                                 order['executedQty'],
                                 order['cummulativeQuoteQty'],
                                 order['status'],
                                 order['timeInForce'],
                                 order['type'],
                                 order['side'],
                                 order['stopPrice'],
                                 order['icebergQty'],
                                 order['origQuoteOrderQty']])
        self.csv_file_name = filename
    # ---- ---- #

    # ---- Open Orders Message Chain ---- #
    def open_orders_message_chain(self, open_orders_list, bot, token):
        if len(open_orders_list) > 0:
            for order in open_orders_list:
                telegram_message = f"Order ID: {order['orderId']}\n" + f"Symbol: {order['symbol']}\n" + f"Price: {order['price']}\n" + f"Original Quantity: {order['origQty']}\n" + f"Executed Quantity: {order['executedQty']}\n" + f"Status: {order['status']}\n" + f"Type: {order['type']}\n" + f"Side: {order['side']}\n" + f"Time In Force: {order['timeInForce']}\n" + f"Stop Price: {order['stopPrice']}"
                bot.send_message(self.chat_id, telegram_message)
        else:
            bot.send_message(self.chat_id, "You have no open orders for " + token)
    # ---- ---- #

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
