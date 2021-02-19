from flask import Flask, request, jsonify
from binance.enums import *
from binance.client import Client

class Binance(object):
    def __init__(self, api_key, secret_key):
        self.client = Client(api_key, secret_key)
        self.client.API_URL = 'https://testnet.binance.vision/api' #only for testing

    def get_account(self):
        ''' Returns account info '''
        account_info = self.client.get_account()
        return account_info

    # ---- Filters Order Requests --- #

    def send_order(self, message):
        order_response = ""
        return order_response
