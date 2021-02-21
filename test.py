raw_message = "/order market buy 5 ltc"

def order_message_filter(message):
    ''' Returns a list of all order parameters: [symbol, side, type, quantity]
    /order {type} {side} {amount} {symbol} -- if limit type -- at {price}'''
    strip_command = message.replace("/order", "").upper()
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

print(order_message_filter(raw_message))
