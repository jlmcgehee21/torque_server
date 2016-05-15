from flask.ext.influxdb import InfluxDB
from flask.ext.httpauth import HTTPBasicAuth

influx_db = InfluxDB()
auth = HTTPBasicAuth()
