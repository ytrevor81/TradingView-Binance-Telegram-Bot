raw_message = "/order stoploss sell 0.5 eth at 1854 stop at 1855"

def order_message_filter(message):
    ''' /order stoploss gtc sell 1 eth at 1964 stop at 1965 '''
    strip_command = message.replace("/order ", "").replace("at ", "").replace("stop ", "").upper()
    order_params = strip_command.split()
    order_type = "STOP_LOSS_LIMIT"
    timeInForce = order_params[1]
    side = order_params[2]
    amount = float(order_params[3])
    sent_symbol = order_params[4]
    if "USDT" in sent_symbol:
        symbol = sent_symbol
    else:
        symbol = sent_symbol + "USDT"
    price = float(order_params[5])
    stopPrice = float(order_params[6])
    return [symbol, side, order_type, timeInForce, amount, price, stopPrice]

print(order_message_filter(raw_message))
