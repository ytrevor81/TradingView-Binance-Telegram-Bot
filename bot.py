import telebot
import threading
import config


class Bot(object):
    def __init__(self):
        self.bot = telebot.TeleBot(config.TELEGRAM_BOT_KEY)

    def error_message(self, symbol, quantity, message_type):
        if message_type == "Denied":
            self.bot.send_message(config.TELEGRAM_ADMIN_ID, "A Binance order for " + str(quantity) + " " + symbol + " has been denied")
        else:
            self.bot.send_message(config.TELEGRAM_ADMIN_ID, "Error: " + message_type)

    def message(self, message):
        self.bot.send_message(config.TELEGRAM_ADMIN_ID, message)

    def test_async(self, bot):
        @bot.message_handler(commands=['start'])
        def check_polling(message):
            bot.reply_to(message, "Helloworld")

    def polling_package(self):
        self.test_async(self.bot)
        self.bot.polling()

    def async_polling(self):
        polling_thread = threading.Thread(target=self.polling_package)
        polling_thread.daemon = True
        polling_thread.start()
