import json, config
from bot import MainBot
from binance_functions import Binance
from message_filter_functions import *
from flask import Flask, request, jsonify

app = Flask(__name__)
bot = MainBot() #Handles all telegram communication


## ---- RECEIVE TRADINGVIEW WEBHOOK AND PLACE ORDER ---- ##
@app.route('/botwebhook', methods=['POST'])
def webhook_process():
    client = Binance(config.SPOTTEST_API_KEY, config.SPOTTEST_SECRET_KEY)
    if bot.block_tradingview:
        bot.message("An order from TradingView has been blocked")
    else:
        data = json.loads(request.data) #Grabs JSON data sent from TradingView via webhook
        if data["passphrase"] == config.PASSPHRASE:
            symbol = data['symbol']
            type = data['type']
            quantity = data['quantity']
            side = data['side'].upper()
            price = data['currentPrice']
            timeInForce = data['timeInForce']
            if type == 'MARKET':
                order_response = client.market_order(symbol, side, type, quantity)
            elif type == 'LIMIT':
                print(symbol, side, type, timeInForce, quantity, price)
                order_response = client.limit_order(symbol, side, type, timeInForce, quantity, price)
            if order_response:
                order_confirmation = order_message(order_response) # Create a confirmation message w/ order details
                bot.message(order_confirmation) #Sends confirmation message via Telegram
                return {
                    'code': 'success'
                        }
            else:
                #bot.error_message(tradingview_symbol, tradingview_quantity, "Denied") #Sends error mesage to admin of Telegram bot
                return {
                    'code': "failed",
                    'message': "Check console log for error"
                       }
        else:
            bot.message("An unauthorized order from TradingView has been blocked. Check your security")
