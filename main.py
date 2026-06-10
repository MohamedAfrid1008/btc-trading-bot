from flask import Flask, request, jsonify
import alpaca_trade_api as tradeapi
import os

app = Flask(__name__)

API_KEY = os.environ.get('ALPACA_API_KEY')
SECRET_KEY = os.environ.get('ALPACA_SECRET_KEY')
BASE_URL = 'https://paper-api.alpaca.markets'

api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

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
        position = api.get_position(symbol)
        has_position = True
    except:
        has_position = False

    if action == 'buy' and not has_position:
        account = api.get_account()
        cash = float(account.cash)
        price = float(data.get('price', 1))
        qty = round((cash * 0.10) / price, 4)  # use 10% of cash
        
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        print(f"BUY order placed: {qty} BTC")

    elif action == 'sell' and has_position:
        api.submit_order(
            symbol=symbol,
            qty=position.qty,
            side='sell',
            type='market',
            time_in_force='gtc'
        )
        print(f"SELL order placed")

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
