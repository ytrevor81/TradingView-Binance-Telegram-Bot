from flask import request, jsonify
from binance.enums import *
from binance.client import Client
from message_filter_functions import *
import csv

class Binance(object):
    def __init__(self, api_key, secret_key):
        self.client = Client(api_key, secret_key)
        self.client.API_URL = 'https://testnet.binance.vision/api' #only for testing

    # ---- Account Info Commands --- #
    def get_account(self):
        ''' Returns account info '''
        recvWindow = { 'recvWindow': 59999 }
        account_info = self.client.get_account(**recvWindow)
        return account_info
    # ---- ---- #

    # ---- Order Commands ---- #
    def send_order(self, order_type, message):
        raw_message = message.text
        if order_type == "limit":
            order_params = limit_order_message_filter(raw_message)
            order_response = self.limit_order(order_params[0], order_params[1], order_params[2], order_params[3], order_params[4], order_params[5])
            order_confirmation = order_message(order_response) #Telegram message sent to user
        elif order_type == "market":
            order_params = market_order_message_filter(raw_message)
            order_response = self.market_order(order_params[0], order_params[1], order_params[2], order_params[3])
            order_confirmation = order_message(order_response) #Telegram message sent to user
        elif order_type =="stoploss":
            order_params = stoploss_order_message_filter(raw_message)
            order_response = self.stoploss_order(order_params[0], order_params[1], order_params[2], order_params[3], order_params[4], order_params[5], order_params[6])
            order_confirmation = stopLoss_message(order_response) #Telegram message sent to user
        print(order_response)
        return order_confirmation

    def market_order(self, symbol, side, order_type, quantity):
        ''' Executes market orders/Depending on type of order commands '''
        try:
            order_dictionary = {'symbol': symbol, 'side': side, 'type': order_type, 'quantity': quantity, 'recvWindow': 59999}
            order = self.client.create_order(**order_dictionary)
        except Exception as e:
            print("something went wrong - {}".format(e))
            #bot.error_message(symbol, quantity, str(e))
            return False

        return order

    def limit_order(self, symbol, side, order_type, timeInForce, quantity, price):
        ''' Executes limit orders/Depending on type of order commands '''
        try:
            order_dictionary = {'symbol': symbol, 'side': side, 'type': order_type, 'timeInForce': timeInForce, 'quantity': quantity, 'price': price, 'recvWindow': 59999}
            order = self.client.create_order(**order_dictionary)
        except Exception as e:
            print("something went wrong - {}".format(e))
            #bot.error_message(symbol, quantity, str(e))
            return False

        return order

    def stoploss_order(self, symbol, side, order_type, timeInForce, quantity, price, stopPrice):
        try:
            order_dictionary = {'symbol': symbol, 'side': side, 'type': order_type, 'timeInForce': timeInForce, 'quantity': quantity, 'price': price, 'stopPrice': stopPrice, 'recvWindow': 59999}
            order = self.client.create_order(**order_dictionary)
        except Exception as e:
            print("something went wrong - {}".format(e))
            #bot.error_message(symbol, quantity, str(e))
            return False

        return order
    # ---- ---- #

    # ---- Check Orders Commands --- #
    def see_all_orders(self, symbol):
        try:
            dict = { 'symbol': symbol, 'recvWindow': 59999 }
            all_orders = self.client.get_all_orders(**dict)
            return all_orders
        except Exception as e:
            print(str(e))
            return 'Whoops'

    def open_orders(self, symbol):
        try:
            dict = { 'symbol': symbol, 'recvWindow': 59999 }
            open_orders = self.client.get_open_orders(**dict)
            print(open_orders)
            return open_orders
        except Exception as e:
            print(str(e))
            return 'Whoops'
    # ---- ---- #

    # ---- Cancel Orders ---- #
    def cancel_order(self, message):
        try:
            cancel_order_params = cancel_order_message_filter(message)
            dict = { 'symbol': cancel_order_params[0], 'orderId': cancel_order_params[1], "recvWindow": 59999 }
            response = self.client.cancel_order(**dict)
            print(response)
            return response
        except Exception as e:
            print(str(e))
