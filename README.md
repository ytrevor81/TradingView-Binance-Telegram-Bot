# TradingView-Binance-Telegram-Bot
Flask | Binance API | Telegram API | TradingView Webhook | JSON

An automated trading bot connecting TradingView alerts via webhook to the Binance API, and sending order confirmations or errors to a Telegram user. The user can also send commands to the bot to make new trades, download trade history, cancel open trades, and a variety of other options! 

## How to run the trading bot
This bot is operated by Flask.

<i>Local Server:</i> After installing the requirements from requirements.txt, open your preferred terminal, navigate into the main directory and type the command "flask run"

<i>Remote Server:</i> After installing Python and the requirements from requirements.txt, configure your server using WSGI. This ensures that your bot is always running. The command "flask run" is not needed for remote servers, unless you want to test the bot in debug mode.

## How does the trading bot work?
There are four parts to this trading bot:
1. Receives TradingView alerts via webhook, at the endpoint "/botwebhook" (found in file <i>app.py</i>)
2. Send order to Binance API (found in file <i>app.py</i>)
3. A Telegram messaging bot sends order confirmations from Binance API and error messages to the Telegram bot admin (found in file <i>bot.py</i>)
4. Send Telegram commands to a Telegram bot connected to the main application.

The user of this trading bot must make a <i>config.py</i> (or a .json file) that holds the desired Binance API keys and the Telegram bot keys. The user must also create a Telegram bot in order to receive notifications from the trading bot.

## TradingView Webhook Alert

Set up your TradingView alert to send a JSON message like this:

{
	"passphrase": "Your passphrase here",
	"time": "{{timenow}}",
	"exchange": "{{exchange}}",
	"symbol": "{{ticker}}",
	"quantity": 1.0,
	"side": "{{strategy.order.action}}",
	"type": "LIMIT",
	"timeInForce": "GTC",
	"currentPrice": {{close}}
}

You can change and add any variable you want, as long as it's in JSON format. Any additions, however, must be added to the Binance API call in <i>app.py</i> as well, because the code in <i>app.py</i> will read directly from this alert message. 

On TradingView, make sure to include the desired url you would like to send in the 'Webhook URL' input (ex: http://your.server.address/botwebhook)


## Telegram Bot

### Commands

1. /start - Saves Chat Id and Username
2. /help - Receive a notification of all valid commands the bot will process.
3. /account - Check current account on Binance
4. /orderhistory {symbol} - Receive a CSV file of all orders made for a specific token (ex. /orderhistory btc)
5. /openorders {symbol} - Checks all open orders for a specific token (ex. /openorders xrp)
6. /market {side} {amount} {symbol} - Place a market order on Binance (ex. /market buy 0.01 eth)
7. /limit {timeInForce} {side} {amount} {symbol} at {price} - Place a limit order on Binance (ex. /limit gtc sell 0.01 eth at 1800)
8. /stoploss {timeInForce} {side} {amount} {symbol} at {price} stop at {stopLoss} - Place a stoploss limit order on Binance (ex. /stoploss gtc sell 0.1 btc at 55000 stop at 54900)
9. /ticker {symbol} - Checks the current price of a given token (ex. /ticker btc)
10. /cancel {symbol} {orderId} - Cancels an open order. It is recommended to call the command /openorders first, so that the user can copy and paste the order ID of a trade they would like to cancel. (ex. /cancel btc 6963)
11. /block - Temporarily blocks automated TradingView orders. This does not block orders made via Telegram command.
12. /unblock - Unblocks automated TradingView orders.

### Order confirmation: 

![Capture](https://user-images.githubusercontent.com/46886041/107135579-81addf80-692e-11eb-842e-4d84e6dc85cc.JPG)

