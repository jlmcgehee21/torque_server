from flask import Flask, render_template, url_for, redirect, request, current_app, Blueprint, jsonify, g, make_response

import datetime
import os
import pandas as pd
import numpy as np

import models
from ..extensions import influx_db, auth
import time
import json

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

        if val.lstrip('-').replace('.','',1).isdigit():
            val = float(val)

        meas = {"measurement": meas_type,
                "tags": {},
                "time": timestamp,
                "fields": {key: val,
                           "session": request.args['session']}
                }

        points.append(meas)

    influx_db.connection.write_points(points)

    return 'OK!'

@api.route('/trips', methods=['GET'])
@auth.login_required
def trips():
    start = request.args.get('start')
    end = request.args.get('end')
    details = request.args.get('details')
    if details is not None:
        details = json.loads(details)

    session_ids = models.TripFinder(start, end).find()

    if details:
        return_dict = {}
        for sesh in session_ids:
            report = models.Trip(sesh).full_report()
            return_dict[sesh] = [reading for reading in report]

        return jsonify(return_dict)

    return jsonify(sessions=[item for item in session_ids])

@api.route('/trips/<trip_id>', methods=['GET'])
@auth.login_required
def trip_details(trip_id, internal=False):
    trip = models.Trip(trip_id)

    summarize = request.args.get('summarize')
    if summarize is not None:
        summarize = json.loads(summarize)

    details = request.args.get('details')
    if details is not None:
        details = json.loads(details)

    if summarize:
        types = request.args.get('measurement_types')
        operation = request.args.get('operation', default='mean')

        summary = trip.summarize(types, operation)

        return jsonify(summary)

    if details:
        readings = trip.full_report()

        return jsonify({trip_id: [reading for reading in readings]})

    else:
        results = trip.overview()

        return jsonify(results)


@api.route('/aggregate', methods=['GET'])
@auth.login_required
def aggregate():

    days_of_history = request.args.get('n_days')
    print days_of_history

    if days_of_history is None:
        start = request.args.get('start')

    else:
        start = pd.to_datetime(datetime.datetime.utcnow()) - pd.Timedelta(days=int(days_of_history))

        start = start.isoformat()

    end = request.args.get('end')
    
    print start, end

    meas_type = request.args.get('measurement_type', 'Trip')
    operation1 = request.args.get('inner', 'max')
    operation2 = request.args.get('outer', 'sum')

    operation_opts = {'sum': sum, 'max': max, 'min': min, 'mean': np.mean}

    operation2 = operation_opts.get(operation2, sum)

    trip_ids = models.TripFinder(start, end).find()

    all_meas = []
    for trip_id in trip_ids:
        meas = models.Trip(trip_id).summarize(meas_type, operation1).get(meas_type)

        if meas is not None:
            all_meas.append(meas[operation1])

    if len(all_meas) > 0:
        response = jsonify({meas_type.replace(' ', ''):
                            np.round(operation2(all_meas), 2)})
    else:
        response = jsonify({meas_type.replace(' ', ''): None})

    return response 


if __name__ == '__main__':
    pass
