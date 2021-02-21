''' All functions here are to filter telegram messages and ensure that the correct syntax is used for each command '''

def market_order_message_filter(message):
    ''' Returns a list of all order parameters: [symbol, side, type, quantity]
    /order {type} {side} {amount} {symbol} symbol, side, order_type, quantity'''
    try:
        strip_command = message.replace("/order ", "").upper()
        order_params = strip_command.split()
        order_type = order_params[0]
        side = order_params[1]
        quantity = float(order_params[2])
        sent_symbol = order_params[3]
        if "USDT" in sent_symbol:
            symbol = sent_symbol
        else:
            symbol = sent_symbol + "USDT"
        return [symbol, side, order_type, quantity]
    except Exception as e:
        return "Syntax Error"

def limit_order_message_filter(message):
    ''' Returns a list of all order parameters: [symbol, side, order_type, timeInForce, quantity, price]
    /order {type} {timeInForce} {side} {amount} {symbol} at {price}'''
    try:
        strip_command = message.replace("/order ", "").replace("at ", "").upper()
        order_params = strip_command.split()
        order_type = order_params[0]
        timeInForce = order_params[1]
        side = order_params[2]
        amount = float(order_params[3])
        sent_symbol = order_params[4]
        if "USDT" in symbol:
            symbol = sent_symbol
        else:
            symbol = sent_symbol + "USDT"
        price = float(order_params[5])
        return [symbol, side, order_type, timeInForce, quantity, price]
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
