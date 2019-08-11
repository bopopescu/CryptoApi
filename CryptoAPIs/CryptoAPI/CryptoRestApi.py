from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS, cross_origin
import json
import requests


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://{user}:{password}@{server}/{database}'.format(user='root', password='root', server='localhost', database='CryptoDB')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
db = SQLAlchemy(app)
ma = Marshmallow(app)


class ExchangeRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dollaramount = db.Column(db.String(80), unique=False)
    datetimeval = db.Column(db.String(120), unique=False)

    def __init__(self, dollaramount, datetimeval):
        self.dollaramount = dollaramount
        self.datetimeval = datetimeval


class ExchangeRateSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('dollaramount', 'datetimeval')




exchange_schema = ExchangeRateSchema()
exchanges_schema = ExchangeRateSchema(many=True)


# endpoint to insert new entry for rate
@app.route("/insert", methods=["GET"])
@cross_origin()
def insert_rate():

    response = requests.get("https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=BTC&to_currency=USD&apikey=F971YDUS70YFOI5Y")
    exchange_ratedata = json.loads(response.text)

    dollaramount = exchange_ratedata["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
    datetimeval = exchange_ratedata["Realtime Currency Exchange Rate"]["6. Last Refreshed"]

    new_entry = ExchangeRate(dollaramount, datetimeval)

    db.session.add(new_entry)
    db.session.commit()
    return None

# endpoint to fetch all data
@app.route("/fetch", methods=["GET"])
@cross_origin()
def get_entries():
    all_entries = ExchangeRate.query.all()
    result = exchanges_schema.dump(all_entries)
    return jsonify(result.data)

if __name__ == '__main__':
    app.run(debug=True)