# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from schedule import similarDB
from travelDB import travelDB
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def main():
    return 'Please enter "server_name/travel/"user_id"/"city"/"days"" at address window.'


@app.route('/travel/<user_id>/<city>/<days>')
@app.route('/travel', defaults={'user_id' : 1, 'city' : 'moscow', 'days' : 3})
def travel(user_id, city, days):
    print('USER ID : {}'.format(user_id))
    print('DESTINATION : {}'.format(city))
    print('DURATION : {}'.format(days))

    similar_db = similarDB(travelDB, user_id, city, days)
    result = similar_db.making_schedule()

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0', port = 5000)
