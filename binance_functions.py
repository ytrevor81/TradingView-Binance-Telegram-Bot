from flask import request, jsonify
from binance.enums import *
from binance.client import Client
from message_filter_functions import *

class Binance(object):
    def __init__(self, api_key, secret_key):
        self.client = Client(api_key, secret_key)
        self.client.API_URL = 'https://testnet.binance.vision/api' #only for testing

        # ---- Account Info Commands --- #
    def get_account(self):
        ''' Returns account info '''
        account_info = self.client.get_account()
        return account_info
        # ---- ---- #

    # ---- Order Commands ---- #
    def send_order(self, message):
        order_params = order_message_filter(message)
        order_type = order_params[0]
        side = order_params[1]
        quantity = order_params[2]
        symbol = order_params[3]
        if len(order_params) > 4: #a long list means that the order is a limit order, not a market order
            price = order_params[4]
            order_response = self.order(symbol, side, order_type, 'GTC', quantity, price)
        else:
            order_response = self.order(symbol, side, order_type, "None", quantity, 0)
        print(order_response)
        order_message = order_message(order_response) #Telegram message sent to user
        return order_message

    def order(self, symbol, side, order_type, timeInForce, quantity, price):
        ''' Executes main orders/Depending on type of order commands '''
        try:
            if price == 0 and timeInForce == "None": #If price == 0, that means the order is a market order
                order_dictionary = {'symbol': symbol, 'side': side, 'type': order_type, 'quantity': quantity, 'recvWindow': 10000}
            else:
                order_dictionary = {'symbol': symbol, 'side': side, 'type': order_type, 'timeInForce': timeInForce, 'quantity': quantity, 'price': price, 'recvWindow': 10000}
            order = self.client.create_order(**order_dictionary)
        except Exception as e:
            print("something went wrong - {}".format(e))
            bot.error_message(symbol, quantity, str(e))
            return False

        return order
    # ---- ---- #


    # ---- Check Orders Commands --- #
    def see_all_orders(self, symbol):
        try:
            dict = {'symbol': symbol}
            all_orders = self.client.get_all_orders(**dict)
            print(all_orders)
            return all_orders
        except Exception as e:
            print(str(e))
            return 'Whoops'

    def open_orders(self, symbol):
        try:
            dict = {'symbol': symbol}
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
            dict = {'symbol': cancel_order_params[0], 'orderId': cancel_order_params[1]}
            response = self.client.cancel_order(**dict)
            print(response)
            return response
        except Exception as e:
            print(str(e))
