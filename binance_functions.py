from flask import request, jsonify
from binance.enums import *
from binance.client import Client
from message_filter_functions import *

class Binance(object):
    def __init__(self, api_key, secret_key):
        self.client = Client(api_key, secret_key)
        self.client.API_URL = 'https://testnet.binance.vision/api' #only for testing

        # ---- /account commands --- #
    def get_account(self):
        ''' Returns account info '''
        account_info = self.client.get_account()
        return account_info
        # ---- ---- #

    # ---- /order commands ---- #
    def send_order(self, message):
        order_params = order_message_filter(message)
        order_type = order_params[0]
        side = order_params[1]
        quantity = order_params[2]
        symbol = order_params[3]
        order_response = self.order(symbol, side, order_type, quantity)
        print(order_response)
        order_message = self.order_message(order_response) #Telegram message sent to user
        return order_message

    def order_message(self, order_response):
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

    def order(self, symbol, side, order_type, quantity):
        ''' Executes main orders/Depending on type of order commands '''
        try:
            order_dictionary = {'symbol': symbol, 'side': side, 'type': order_type, 'quantity': quantity, 'recvWindow': 10000}
            order = self.client.create_order(**order_dictionary)
        except Exception as e:
            print("something went wrong - {}".format(e))
            bot.error_message(symbol, quantity, str(e))
            return False

        return order
