import logging
import requests
import sqlite3 as sql
from hashlib import sha256
from datetime import datetime
from logging.handlers import RotatingFileHandler
from flask import Flask, request, render_template, redirect

app = Flask(__name__)
app.config.from_pyfile('static/config.py', silent=True)

# handler = RotatingFileHandler('test_task.log', maxBytes=10000, backupCount=1)
# handler.setLevel(logging.INFO)
# app.logger.addHandler(handler)


@app.route('/', methods=['GET'])
def my_form():
    return render_template('my-form.html')


@app.route('/', methods=['POST'])
def my_form_post():
    amount = request.form['sum']
    currency = request.form['currency']
    # app.logger.info('POST -- {} - {}'.format(amount, currency))
    shop_order_id = "101"
    if amount.replace('.', '', 1).isdigit():
        if currency == '978':
            params = {
                'amount': amount,
                'currency': currency,
                'shop_id': app.config['SHOP_ID'],
                'shop_order_id': shop_order_id
            }
            params['sign'] = get_sign(params)
            params['description'] = 'Test task'
            # app.logger.info('Redirect for EUR')
            add_to_db(amount, 'EUR', True)
            return render_template('pay.html',
                                   **params)

        elif currency == '840':
            request_data = {
                "payer_currency": currency,
                "shop_amount": amount,
                "shop_currency": currency,
                "shop_id": app.config['SHOP_ID'],
                "shop_order_id": shop_order_id
            }
            request_data['sign'] = get_sign(request_data)
            response = requests.post('https://core.piastrix.com/bill/create',
                                     json=request_data,
                                     headers={'Content-Type': 'application/json'}).json()
            # app.logger.info('Redirect for USD')

            if response['result']:
                add_to_db(amount, 'USD', True)
                return redirect(response['data']['url'], code=302)
            else:
                # app.logger.info('Error -- {}'.format(response['message']))
                add_to_db(amount, 'USD', False)
                return render_template('my-form.html', message='Something went wrong :(')

        else:
            request_data = {
                "amount": amount,
                "currency": currency,
                "payway": app.config['PAYWAY'],
                "shop_id": app.config['SHOP_ID'],
                "shop_order_id": shop_order_id
            }
            request_data['sign'] = get_sign(request_data)
            response = requests.post('https://core.piastrix.com/invoice/create',
                                     json=request_data,
                                     headers={'Content-Type': 'application/json'}).json()
            # app.logger.info('Redirect for RUB')

            if response['result']:
                response = response['data']
                add_to_db(amount, 'RUB', True)
                return render_template('invoice.html',
                                       method=response['method'],
                                       **response['data'])
            else:
                # app.logger.info('Error -- {}'.format(response['message']))
                add_to_db(amount, 'RUB', False)
                return render_template('my-form.html', message='Something went wrong :(')
    return render_template('my-form.html', message='Enter correct number!')


def get_sign(sign_params: dict):
    sign = [str(sign_params[param]) for param in sorted(sign_params.keys())]
    sign = ':'.join(sign) + app.config['SECRET_KEY']
    sign = sha256(sign.encode('utf-8')).hexdigest()
    return sign


def add_to_db(amount, currency, status: bool):
    status = str(int(status))
    currency = '"' + currency + '"'
    date = datetime.today().strftime('"%Y-%m-%d %H:%M:%S"')
    with sql.connect('database.db') as con:
        cursor = con.cursor()
        cursor.execute('''
        INSERT INTO Payments(`amount`, `currency`, `date`, `status`)
        VALUES ({})'''.format(', '.join([str(amount), currency, date, status])))
        con.commit()


if __name__ == '__main__':
    app.run(host='0.0.0.0')
