from db_functions import Database
from binance_functions import Binance
from telegram.ext import *
import threading, config, requests, csv, os, telebot
from message_filter_functions import *
'''This is the complete Telegram bot. Trading functions are not included here'''

class MainBot(object):
    def __init__(self):
        self.client = Binance(config.SPOTTEST_API_KEY, config.SPOTTEST_SECRET_KEY)
        self.chat_id = None #will be assigned via message
        self.user_name_recorded = False
        self.ticker_link = 'https://api.binance.com/api/v3/ticker/price?symbol=' #need to add symbol to the end
        self.general_error_message = "Incorrect syntax or symbol. Please see example below or see /help \n\n" # Add onto the end of this message the specific command syntax needed
        self.csv_file_name = None #this will automatically delete any csv file called on /orderhistory
        self.block_tradingview = False #if True, TradingView orders will be blocked

        # ---- Initializing Functions --- #
        self.bot = telebot.TeleBot(config.TELEGRAM_BOT_KEY)
        self.updater = Updater(config.TELEGRAM_BOT_KEY, use_context=True)
        self.dp = self.updater.dispatcher
        self.initial_chat_id_check() #checks if chat_id is already in the DB
        #self.all_bot_actions()
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
        username = message.from_user.first_name
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

    def initialize_bot(self, update, context):
        #Start Command: /start
        DB = Database()
        message = update.message
        if self.correct_user(message, DB):
            chat_id = message.chat.id
            DB.save_chat_id(chat_id)
            self.chat_id = chat_id
            message.reply_text("Hello " + message.from_user.first_name)
            #bot.reply_to(message, "Hello " + message.from_user.first_name)

    def bot_info(self, update, context):
        #Help Command: /help
        DB = Database()
        message = update.message
        if self.correct_user(message, DB):
            help = help_message()
            message.reply_text(help)
            #bot.reply_to(message, help)

    def make_market_order(self, update, context):
        #Market order: /market {side} {amount} {symbol}
        DB = Database()
        message = update.message
        if self.correct_user(message, DB):
            try:
                order_confirmation = self.client.send_order("market", message)
                message.reply_text(order_confirmation)
            except Exception as e:
                print(str(e))
                message.reply_text(self.general_error_message + "ex. /market buy 0.01 eth \n\n/market {side} {amount} {symbol}")
                #bot.reply_to(message, self.general_error_message + "ex. /market buy 0.01 eth \n\n/market {side} {amount} {symbol}")

    def make_limit_order(self, update, context):
        #Limit order: /limit {timeInForce} {side} {amount} {symbol} at {price}
        DB = Database()
        message = update.message
        if self.correct_user(message, DB):
            try:
                order_confirmation = self.client.send_order("limit", message)
                message.reply_text(order_confirmation)
                #bot.reply_to(message, order_confirmation)
            except Exception as e:
                print(str(e))
                message.reply_text(self.general_error_message + "ex. /limit gtc sell 0.01 ethusdt at 1858 \n\n/limit {timeInForce} {side} {amount} {symbol} at {price}")
                #bot.reply_to(message, self.general_error_message + "ex. /limit gtc sell 0.01 ethusdt at 1858 \n\n/limit {timeInForce} {side} {amount} {symbol} at {price}")

    def make_stoploss_order(self, update, context):
        #'''Makes only one order: /stoploss {timeInForce} {side} {amount} {symbol} at {price} stop at {stopLoss}'''
        DB = Database()
        message = update.message
        if self.correct_user(message, DB):
            try:
                order_confirmation = self.client.send_order("stoploss", message)
                message.reply_text(order_confirmation)
                #bot.reply_to(message, order_confirmation)
            except Exception as e:
                print(str(e))
                message.reply_text(self.general_error_message + "ex. /stoploss gtc sell 0.1 btc at 55000 stop at 56000\n\n /stoploss {timeInForce} {side} {amount} {symbol} at {price} stop at {stopLoss}")
                #bot.reply_to(message, self.general_error_message + "ex. /stoploss gtc sell 0.1 btc at 55000 stop at 56000\n\n /stoploss {timeInForce} {side} {amount} {symbol} at {price} stop at {stopLoss}")

    def current_price(self, update, context):
        #''' Checks current price of a token '''
        DB = Database()
        message = update.message
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
                message.reply_text(data['symbol'] + ": " + data['price'])
                #bot.reply_to(message, data['symbol'] + ": " + data['price'])
            except Exception as e:
                message.reply_text(self.general_error_message + "ex. /ticker btc or /ticker btcusdt")
                #bot.reply_to(message, self.general_error_message + "ex. /ticker btc or /ticker btcusdt")

    def show_order_history(self, update, context):
        #''' View order history: /orderhistory
        #Sends a csv of their past orders'''
        DB = Database()
        message = update.message
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
                self.bot.send_document(self.chat_id, doc)
            except Exception as e:
                print(str(e))
                message.reply_text(self.general_error_message + " AND make sure that you have made orders in the past using the token in question\n\nex. /orderhistory btc \n\n/orderhistory {symbol}")
                #bot.reply_to(message, self.general_error_message + "ex. /orderhistory btc \n\n/orderhistory {symbol}\n\nAlso make sure that you have made orders in the past using the token in question")

    def show_open_orders(self, update, context):
        #''' View open orders for a given token: /openorders {symbol}'''
        DB = Database()
        message = update.message
        if self.correct_user(message, DB):
            try:
                quick_token_text = message.text.replace("/openorders", "").replace(" ", "").upper()
                if "USDT" in quick_token_text:
                    token = quick_token_text
                else:
                    token = quick_token_text + "USDT"
                open_orders = self.client.open_orders(token)
                self.open_orders_message_chain(open_orders, self.bot, token)
            except Exception as e:
                print(str(e))
                message.reply_text(self.general_error_message + "ex. /openorders eth\n\n/openorders {symbol}\n\nAlso make sure that you have made orders in the past using the token in question")
                #bot.reply_to(message, self.general_error_message + "ex. /openorders eth\n\n/openorders {symbol}\n\nAlso make sure that you have made orders in the past using the token in question")

    def cancel_order(self, update, context):
        #'''Cancels an order /cancel {symbol} {orderId}'''
        DB = Database()
        message = update.message
        if self.correct_user(message, DB):
            try:
                cancelled_order = self.client.cancel_order(message)
                cancel_message = cancelled_message(cancelled_order)
                message.reply_text(cancel_message)
                #bot.reply_to(message, cancel_message)
            except Exception as e:
                print(str(e))
                message.reply_text(self.general_error_message + "ex. /cancel eth 6963\n\n/cancel {symbol} {order Id}\n\n")
                #bot.reply_to(message, self.general_error_message + "ex. /cancel eth 6963\n\n/cancel {symbol} {order Id}\n\n")

    def show_account(self, update, context):
        DB = Database()
        message = update.message
        if self.correct_user(message, DB):
            info = self.client.get_account()
            message.reply_text(str(info))
            #bot.reply_to(message, str(info))

    def block_tradingview_orders(self, update, context):
        #''' Temporarily blocks tradingview orders '''
        DB = Database()
        message = update.message
        if self.correct_user(message, DB):
            if self.block_tradingview:
                message.reply_text("TradingView orders are already blocked. /unblock to continue TradingView orders")
                #bot.reply_to(message, "TradingView orders are already blocked. /unblock to continue TradingView orders")
            else:
                self.block_tradingview = True
                message.reply_text("TradingView orders are now blocked. /unblock to continue TradingView orders")
                #bot.reply_to(message, "TradingView orders are now blocked. /unblock to continue TradingView orders")

    def unblock_tradingview_orders(self, update, context):
        #''' Unblocks tradingview orders '''
        DB = Database()
        message = update.message
        if self.correct_user(message, DB):
            if self.block_tradingview:
                self.block_tradingview = False
                message.reply_text("TradingView orders ready to continue. /block to block TradingView orders")
                #bot.reply_to(message, "TradingView orders ready to continue. /block to block TradingView orders")
            else:
                message.reply_text("TradingView orders are currently active. /block to block TradingView orders")
                #bot.reply_to(message, "TradingView orders are currently active. /block to block TradingView orders")

    def kill_app(self, update, context):
        #''' Block TradingView orders and raises an Exception, killing the current Bot thread '''
        self.block_tradingview = True
        #self.bot_running = False
        #self.bot.stop_polling()
        pass
        #bot.send_message(0, message)

    def bot_commands(self):
        self.dp.add_handler(CommandHandler("start", self.initialize_bot))
        self.dp.add_handler(CommandHandler("help", self.bot_info))
        self.dp.add_handler(CommandHandler("market", self.make_market_order))
        self.dp.add_handler(CommandHandler("limit", self.make_limit_order))
        self.dp.add_handler(CommandHandler("stoploss", self.make_stoploss_order))
        self.dp.add_handler(CommandHandler("ticker", self.current_price))
        self.dp.add_handler(CommandHandler("orderhistory", self.show_order_history))
        self.dp.add_handler(CommandHandler("openorders", self.show_open_orders))
        self.dp.add_handler(CommandHandler("cancel", self.cancel_order))
        self.dp.add_handler(CommandHandler("account", self.show_account))
        self.dp.add_handler(CommandHandler("block", self.block_tradingview_orders))
        self.dp.add_handler(CommandHandler("unblock", self.unblock_tradingview_orders))
        self.dp.add_handler(CommandHandler("kill", self.kill_app))

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
    def polling(self):
        self.updater.start_polling()
        #self.updater.idle()

    def all_bot_actions(self):
        self.bot_commands()
        self.polling()

    def restart_async_polling(self):
        self.polling_thread = threading.Thread(target=self.all_bot_actions)
        self.polling_thread.start()

    def stop_async_polling(self):
        self.updater.stop_polling()
        self.polling_thread.join()

    # ---- ---- #
