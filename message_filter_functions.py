''' All functions here are to filter telegram messages and ensure that the correct syntax is used for each command '''

def order_message_filter(message):
    ''' Returns a list of all order parameters: [symbol, side, type, quantity]
    /order {type} {side} {amount} {symbol} -- if limit type -- at {price}'''
    try:
        strip_command = message.text.replace("/order", "").upper()
        order_params = strip_command.split()
        order_params[2] = float(order_params[2])
        return order_params
    except Exception as e:
        return "Syntax Error"
