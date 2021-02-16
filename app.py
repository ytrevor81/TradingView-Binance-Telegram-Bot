import json, config
from bot import Bot
from binance.client import Client
from flask import Flask, request, jsonify
from binance.enums import *
import telebot
import threading


app = Flask(__name__)
client = Client(config.SPOTTEST_API_KEY, config.SPOTTEST_SECRET_KEY) # Client object for executing orders on Binance API
client.API_URL = 'https://testnet.binance.vision/api' #Test via Binance Spot Test API
bot = Bot() #Handles all telegram communication
#test_bot = telebot.TeleBot(config.TELEGRAM_BOT_KEY)


## ---- BINANCE API ---- ##
def order(symbol, side, order_type, quantity):
    ''' This function tests basic orders. More complex orders can be made by making additions and changes to the order_dictionary. '''
    try:
        order_dictionary = {'symbol': symbol, 'side': side, 'type': order_type, 'quantity': quantity, 'recvWindow': 10000}
        order = client.create_order(**order_dictionary)
    except Exception as e:
        print("something went wrong - {}".format(e))
        bot.error_message(symbol, quantity, str(e))
        return False

    return order

def order_message(order_response):
    ''' This function creates a message confirming an order w/ details via Telegram '''
    #Main order info
    orderId = order_response["orderId"]
    symbol = order_response["symbol"]
    clientOrderId = order_response["clientOrderId"]
    origQty = order_response["origQty"]
    executedQty = order_response["executedQty"]
    status = order_response["status"]
    cummulativeQuoteQty = order_response["cummulativeQuoteQty"]
    type = order_response["type"]
    side = order_response["side"]

    #Fill info
    price = order_response["fills"][0]["price"]
    qty = order_response["fills"][0]["qty"]
    commission = order_response["fills"][0]["commission"]
    commissionAsset = order_response["fills"][0]["commissionAsset"]
    tradeId = order_response["fills"][0]["tradeId"]

    order_message = f"Order ID: {orderId}\n" + f"Symbol: {symbol}\n" + f"Client Order ID: {clientOrderId}\n" + f"Original Quantity ID: {origQty}\n" + f"Executed Quantity ID: {executedQty}\n" + f"Status: {status}\n" + f"Cummulative Quote Quantity ID: {cummulativeQuoteQty}\n" + f"Type: {type}\n" + f"Side: {side}\n\n" + "Fill: \n" f"Price: {price}\n" + f"Quantity: {qty}\n" + f"Commission: {commission}\n" + f"Commission Asset: {commissionAsset}\n" + f"Trade ID: {tradeId}"
    return order_message
## ---- ---- ##


## ---- RECEIVE TRADINGVIEW WEBHOOK AND PLACE ORDER ---- ##
@app.route('/atbwebhook', methods=['POST'])
def webhook_process():
    data = json.loads(request.data) #Grabs JSON data sent from TradingView via webhook

    '''Variables from the TradingView webhook: any other indicators the client wants can be sent through the TradingView webhook'''
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

#Asynchronous Running bot
#polling_thread = threading.Thread(target=async_polling)
#polling_thread.daemon = True
#polling_thread.start()
bot.async_polling()
