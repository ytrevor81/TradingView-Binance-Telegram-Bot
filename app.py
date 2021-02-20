import json, config
from bot import Bot
from binance.client import Client
from flask import Flask, request, jsonify
from binance.enums import *

app = Flask(__name__)
client = Client(config.SPOTTEST_API_KEY, config.SPOTTEST_SECRET_KEY) # Client object for executing orders on Binance API
client.API_URL = 'https://testnet.binance.vision/api' #Test via Binance Spot Test API
bot = Bot() #Handles all telegram communication


## ---- BINANCE API ---- ##


## ---- ---- ##


## ---- RECEIVE TRADINGVIEW WEBHOOK AND PLACE ORDER ---- ##
'''
@app.route('/botwebhook', methods=['POST'])
def webhook_process():
    data = json.loads(request.data) #Grabs JSON data sent from TradingView via webhook

    tradingview_symbol = data['symbol']
    tradingview_quantity = data['quantity']
    tradingview_side = data['side']
    order_response = order(tradingview_symbol, tradingview_side, Client.ORDER_TYPE_MARKET, tradingview_quantity)

    if order_response and len(order_response) > 1:
        order_confirmation = order_message(order_response) # Create a confirmation message w/ order details
        bot.message(str(order_confirmation)) #Sends confirmation message via Telegram
        return {
            'code': 'success'
                }
    else:
        bot.error_message(tradingview_symbol, tradingview_quantity, "Denied") #Sends error mesage to admin of Telegram bot
        return {
            'code': "failed",
            'message': "Check console log for error"
               }
'''
