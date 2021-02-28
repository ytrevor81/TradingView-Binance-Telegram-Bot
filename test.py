from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import config

def start(update, context):
    """Send a message when the command /start is issued."""
    user = update.message.from_user.username
    update.message.reply_text('Hi ' + user + "!")


def help(update, context):
    """Send a message when the command /help is issued."""
    message = update.message.text.replace("/help", "")

    update.message.reply_text(message + " !!!!!")


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)



def main():
    """Start the bot."""

    updater = Updater(config.TELEGRAM_BOT_KEY, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))


    # Start the Bot
    updater.start_polling()
    updater.idle()

main()

'''

@bot.message_handler(commands=['start'])
def initialize_bot(message):
    DB = Database()
    if self.correct_user(message, DB):
        chat_id = message.chat.id
        DB.save_chat_id(chat_id)
        self.chat_id = chat_id
        bot.reply_to(message, "Hello " + message.from_user.first_name)

@bot.message_handler(commands=['help'])
def bot_info(message):
    DB = Database()
    if self.correct_user(message, DB):
        help = help_message()
        bot.reply_to(message, help)

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
            bot.reply_to(message, self.general_error_message + "ex. /market buy 0.01 eth \n\n/market {side} {amount} {symbol}")

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
            bot.reply_to(message, self.general_error_message + "ex. /limit gtc sell 0.01 ethusdt at 1858 \n\n/limit {timeInForce} {side} {amount} {symbol} at {price}")

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
            bot.reply_to(message, self.general_error_message + "ex. /stoploss gtc sell 0.1 btc at 55000 stop at 56000\n\n /stoploss {timeInForce} {side} {amount} {symbol} at {price} stop at {stopLoss}")

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

@bot.message_handler(commands=['block'])
def block_tradingview_orders(message):
    ''' Temporarily blocks tradingview orders '''
    DB = Database()
    if self.correct_user(message, DB):
        if self.block_tradingview:
            bot.reply_to(message, "TradingView orders are already blocked. /unblock to continue TradingView orders")
        else:
            self.block_tradingview = True
            bot.reply_to(message, "TradingView orders are now blocked. /unblock to continue TradingView orders")

@bot.message_handler(commands=['unblock'])
def unblock_tradingview_orders(message):
    ''' Unblocks tradingview orders '''
    DB = Database()
    if self.correct_user(message, DB):
        if self.block_tradingview:
            self.block_tradingview = False
            bot.reply_to(message, "TradingView orders ready to continue. /block to block TradingView orders")
        else:
            bot.reply_to(message, "TradingView orders are currently active. /block to block TradingView orders")

@bot.message_handler(commands=['kill'])
def kill_app(message):
    ''' Block TradingView orders and raises an Exception, killing the current Bot thread '''
    self.block_tradingview = True
    self.bot_running = False
    self.bot.stop_polling()
    bot.send_message(0, message)



'''
