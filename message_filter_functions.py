''' All functions here are to filter telegram messages and ensure that the correct syntax is used for each command '''

def market_order_message_filter(message):
    ''' Returns a list of all order parameters: [symbol, side, type, quantity]
    /order {type} {side} {amount} {symbol} symbol, side, order_type, quantity'''
    try:
        strip_command = message.replace("/market ", "").upper()
        order_params = strip_command.split()
        order_type = "MARKET"
        side = order_params[0]
        quantity = float(order_params[1])
        sent_symbol = order_params[2]
        if "USDT" in sent_symbol:
            symbol = sent_symbol
        else:
            symbol = sent_symbol + "USDT"
        return [symbol, side, order_type, quantity]
    except Exception as e:
        return "Syntax Error"

def limit_order_message_filter(message):
    ''' Returns a list of all order parameters: [symbol, side, order_type, timeInForce, quantity, price]
    /limit {type} {timeInForce} {side} {amount} {symbol} at {price}   /limit gtc sell 1000 xrp at 0.59'''
    try:
        strip_command = message.replace("/limit ", "").replace("at ", "").upper()
        order_params = strip_command.split()
        order_type = "LIMIT"
        timeInForce = order_params[0]
        side = order_params[1]
        amount = float(order_params[2])
        sent_symbol = order_params[3]
        if "USDT" in sent_symbol:
            symbol = sent_symbol
        else:
            symbol = sent_symbol + "USDT"
        price = float(order_params[4])
        return [symbol, side, order_type, timeInForce, amount, price]
    except Exception as e:
        return "Syntax Error"

def stoploss_order_message_filter(message):
    ''' Returns a list of all order parameters: [symbol, side, order_type, timeInForce, quantity, price]
    /order {type} {timeInForce} {side} {amount} {symbol} at {price} stop at {stopPrice}'''
    try:
        strip_command = message.replace("/stoploss ", "").replace("at ", "").replace("stop ", "").upper()
        order_params = strip_command.split()
        order_type = "STOP_LOSS_LIMIT"
        timeInForce = order_params[0]
        side = order_params[1]
        amount = float(order_params[2])
        sent_symbol = order_params[3]
        if "USDT" in sent_symbol:
            symbol = sent_symbol
        else:
            symbol = sent_symbol + "USDT"
        price = float(order_params[4])
        stopPrice = float(order_params[5])
        return [symbol, side, order_type, timeInForce, amount, price, stopPrice]
    except Exception as e:
        return "Syntax Error"

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
    if len(order_response["fills"]) < 1:
        telegram_message = f"Order ID: {orderId}\n" + f"Symbol: {symbol}\n" + f"Client Order ID: {clientOrderId}\n" + f"Original Quantity ID: {origQty}\n" + f"Executed Quantity ID: {executedQty}\n" + f"Status: {status}\n" + f"Cummulative Quote Quantity ID: {cummulativeQuoteQty}\n" + f"Type: {type}\n" + f"Side: {side}\n\n"
        return telegram_message
    else:
        price = order_response["fills"][0]["price"]
        qty = order_response["fills"][0]["qty"]
        commission = order_response["fills"][0]["commission"]
        commissionAsset = order_response["fills"][0]["commissionAsset"]
        tradeId = order_response["fills"][0]["tradeId"]

        telegram_message = f"Order ID: {orderId}\n" + f"Symbol: {symbol}\n" + f"Client Order ID: {clientOrderId}\n" + f"Original Quantity ID: {origQty}\n" + f"Executed Quantity ID: {executedQty}\n" + f"Status: {status}\n" + f"Cummulative Quote Quantity ID: {cummulativeQuoteQty}\n" + f"Type: {type}\n" + f"Side: {side}\n\n" + "Fill: \n" f"Price: {price}\n" + f"Quantity: {qty}\n" + f"Commission: {commission}\n" + f"Commission Asset: {commissionAsset}\n" + f"Trade ID: {tradeId}"
        return telegram_message

def stopLoss_message(order_response):
    orderId = order_response["orderId"]
    symbol = order_response["symbol"]
    clientOrderId = order_response["clientOrderId"]
    side = "STOP LOSS LIMIT"

    telegram_message = f"Order ID: {orderId}\n" + f"Symbol: {symbol}\n" + f"Client Order ID: {clientOrderId}\n" + f"Side: {side}"
    return telegram_message

def cancelled_message(order_response):
    try:
        orderId = order_response["orderId"]
        symbol = order_response["symbol"]
        price = order_response["price"]
        origQty = order_response["origQty"]
        executedQty = order_response["executedQty"]
        status = order_response["status"]
        type = order_response["type"]
        side = order_response["side"]
        timeInForce = order_response["timeInForce"]

        telegram_message = f"Status: {status}\n" + f"Order ID: {orderId}\n" + f"Symbol: {symbol}\n" + f"Price: {price}\n" + f"Original Quantity ID: {origQty}\n" + f"Executed Quantity ID: {executedQty}\n" + f"Type: {type}\n" + f"Side: {side}\n" + f"Time In Force: {timeInForce}\n"
        return telegram_message
    except Exception as e:
        print(e)

def cancel_order_message_filter(message):
    ''' Returns a list of all cancel_order parameters: [symbol, orderId]
    /cancel {symbol} {orderId}'''
    strip_command = message.text.replace("/cancel", "")
    cancel_order_params = strip_command.split()
    symbol = cancel_order_params[0].upper()
    if "USDT" in symbol:
        cancel_order_params[0] = symbol
    else:
        cancel_order_params[0] = symbol + "USDT"
    return cancel_order_params

def help_message():
    account = "- Check account: /account\n\n"
    order_history = "- CSV of your order history for a given token:\n /orderhistory {symbol} (ex. /orderhistory eth)\n\n"
    open_orders = "- Check all open orders for a given token:\n /openorders {symbol} (ex. /opensorders btc)\n\n"
    market_order = "- Make a market order:\n /market {side} {amount} {symbol} ( ex. /market buy 0.01 eth )\n\n"
    limit_order = "- Make a limit order:\n /limit {timeInForce} {side} {amount} {symbol} at {price} ( ex. /limit gtc sell 0.01 ethusdt at 1858 )\n\n"
    stoploss_order = "- Make a stop loss order:\n /stoploss {timeInForce} {side} {amount} {symbol} at {price} stop at {stopLoss} ( ex. /stoploss gtc sell 0.1 btc at 55000 stop at 56000 )\n\n"
    ticker = "- Check current price of token:\n /ticker {symbol}( ex. /ticker trx )\n\n"
    cancel_order = "- Cancels an open order. *Call /openorders first to see the order IDs:\n /cancel {symbol} {orderId} ( ex. /cancel eth 6963 )\n\n"
    block_tradingview = "- Temporarily block TradingView orders: /block\n\n"
    unblock_tradingview = "- Unblock TradingView orders: /unblock"
    return account + order_history + open_orders + market_order + limit_order + stoploss_order + ticker + cancel_order + block_tradingview + unblock_tradingview
