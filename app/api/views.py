from flask import Flask, render_template, url_for, redirect, request, current_app, Blueprint, jsonify, g, make_response

import datetime
import os


import models
from ..extensions import influx_db, auth
import time


app = current_app

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)


api = Blueprint('api', __name__, template_folder='templates', url_prefix='/api')


@api.route('/')
@auth.login_required
def main_page():
    return jsonify({'status_code': 200})

@api.route('/torque', methods=['GET'])
def process_torque_data():
    if app.config['TORQUE_EMAIL'] != request.args.get('eml'):
        return 'Unauthorized', 401

    reading_time = request.args['time']
    reading_time = float(reading_time[:10]+'.'+reading_time[10:])
    timestamp = datetime.datetime.fromtimestamp(reading_time)

    meas_type = "torque_reading"
    if 'user' in ''.join(request.args.keys()):
        meas_type = "session_start"

    points = []
    for key, val in request.args.iteritems():
        if key in ['time', 'session']:
            continue

        meas = {"measurement": meas_type,
                "tags": {},
                "time": timestamp,
                "fields": {key: val,
                           "session": request.args['session']}
                }

        points.append(meas)

    influx_db.connection.write_points(points)

    return 'OK!'


if __name__ == '__main__':
    pass
