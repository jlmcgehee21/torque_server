from ..extensions import influx_db
from fuzzywuzzy import fuzz
import pandas as pd


class TripFinder(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def find(self):
        session_query_str = 'select distinc(session) from session_start '

        where_clause = 'where '
        if self.start is not None:
            start_str = pd.to_datetime(self.start).isoformat()+'Z'
            where_clause += 'time > \'{}\' '.format(start_str)

        if self.end is not None:
            if start_str is not None:
                where_clause += 'and '

            end_str = pd.to_datetime(self.end).isoformat()+'Z'
            where_clause += 'time < \'{}\' '.format(end_str)

        if any([var is not None for var in [self.start, self.end]]):
            session_query_str += where_clause

        results = influx_db.connection.query(session_query_str)['session_start']

        for item in results:
            yield item['distinct']


class Trip(object):
    def __init__(self, trip_id):
        self.trip_id = trip_id

    @property
    def info_map(self):
        query_string = 'select * from session_start\
                        where session=\'{}\''.format(self.trip_id)

        readings = influx_db.connection.query(query_string)['session_start']
        session_info = readings.next()

        info_map = {}
        info_map['names'] = dict(filter(lambda kv: 'ShortName' in kv[0],
                                        session_info.iteritems()))
        info_map['names'] = dict(map(lambda kv: (kv[0].split('Name')[-1], kv[1]),
                                     info_map['names'].iteritems()))

        info_map['units'] = dict(filter(lambda kv: 'Unit' in kv[0],
                                        session_info.iteritems()))
        info_map['units'] = dict(map(lambda kv: (kv[0].split('Unit')[-1], kv[1]),
                                     info_map['units'].iteritems()))

        return info_map


    def full_report(self):
        """
        :returns: iterator of all readings
        """
        query_string = 'select * from torque_reading\
                        where session=\'{}\''.format(self.trip_id)

        readings = influx_db.connection.query(query_string)['torque_reading']
        return readings



    def summarize(self, measurement_types, operation):
        """
        :param measurement_types: list of strings that will be fuzzy matched to
                                  friendly measurement names.

        :param operation: string matching influx operation you wish to do on
                          measurements returned.
        """

        if measurement_types is not None:
            types = measurement_types.split(',')
            fields = []
            names = []
            for meas, name in self.info_map['names'].iteritems():
                if any([fuzz.ratio(name, item) >= 98 for item in types]):
                    fields.append(meas)
                    names.append(name)

                elif any([fuzz.partial_ratio(name, item) > 50 for item in types]):
                    fields.append(meas)
                    names.append(name)
        else:
            fields = self.info_map['names'].keys()
            names = [self.info_map['names'][key] for key in fields]

        if operation == 'range':
            queries = ['select max(k{})-min(k{}) from\
                        torque_reading where\
                        session=\'{}\''.format(field,
                                               field,
                                               self.trip_id) for field in fields]

        else:
            queries = ['select {}(k{}) from\
                        torque_reading where\
                        session=\'{}\''.format(operation,
                                               field,
                                               self.trip_id) for field in fields]

        results = [influx_db.connection.query(query) for query in queries]

        output = {}
        for ind, result in enumerate(results):
            if len(result.items()) > 0:
                output[names[ind]] = result['torque_reading'].next()
                output[names[ind]]['unit'] = self.info_map['units'][fields[ind]]

        return output


    def overview(self):
        info = {'measurements': []}
        for key in self.info_map['names']:
            info['measurements'].append(u'{} ({})'.format(self.info_map['names'][key],
                                                         self.info_map['units'][key]))

        maxes = self.summarize('Trip,Spd,Boost', 'max')

        for k, v in maxes.iteritems():
            info[k] = v

        return info
