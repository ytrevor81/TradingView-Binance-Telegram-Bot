def order_message_filter():
    ''' Returns a list of all order parameters: [symbol, side, type, quantity]
    /order {type} {side} {amount} {symbol} -- if limit type -- at {price}'''
    message = "/order market buy 0.5 btcusdt"
    strip_command = message.replace("/order", "").upper()
    print(strip_command)
    list_of_strings = strip_command.split()
    list_of_strings[2] = float(list_of_strings[2])
    print(list_of_strings)

order_message_filter()
