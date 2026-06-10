from flask import Flask, request, jsonify
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import os

app = Flask(__name__)

API_KEY = os.environ.get('ALPACA_API_KEY')
SECRET_KEY = os.environ.get('ALPACA_SECRET_KEY')

client = TradingClient(API_KEY, SECRET_KEY, paper=True)

@app.route('/')
def home():
    return 'Bot is running'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"Signal received: {data}")

    symbol = 'BTCUSD'
    action = data.get('action')

    try:
        position = client.get_open_position(symbol)
        has_position = True
    except:
        has_position = False

    if action == 'buy' and not has_position:
        account = client.get_account()
        cash = float(account.cash)
        price = float(data.get('price', 1))
        qty = round((cash * 0.10) / price, 4)

        order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.GTC
        )
        client.submit_order(order)
        print(f"BUY order placed: {qty} BTC")

    elif action == 'sell' and has_position:
        qty = position.qty
        order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.GTC
        )
        client.submit_order(order)
        print(f"SELL order placed")

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
