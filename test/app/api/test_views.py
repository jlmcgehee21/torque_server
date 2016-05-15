import unittest
from app import create_app as ca
from app.config import TestConfig
from flask import Flask, url_for
from flask.ext.testing import TestCase, LiveServerTestCase
import urllib2
import os
import base64
import urllib

SESSION_START = ('/api/torque?eml={}'
                 '&v=8&session=1463186875158&'
                 'id=d6adrjheu2937g23igakdfdf'
                 '&time=1463186875171&userUnitff1005=&deg'
                 '&userUnitff1006=&deg&userUnitff1001=mph'
                 '&userUnitff1007=&userUnit04=%20&userShortName04=Load'
                 '&userFullName04=Engine%20Load&userUnit0c=rpm'
                 '&userShortName0c=Revs&userFullName0c=Engine%20RPM'
                 '&userUnitff1226=hp&userShortNameff1226=HP'
                 '&userFullNameff1226=Horsepower%20(At%20the%20wheels)'
                 '&userUnit0f=&degF&userShortName0f=Intake'
                 '&userFullName0f=Intake%20Air%20Temperature&userUnit10=g'
                 '%2Fs&userShortName10=MAF&u'
                 'serFullName10=Mass%20Air%20Flow%20Rate&userUnitff1001=mph'
                 '&userShortNameff1001=GPS%20Spd'
                 '&userFullNameff1001=Speed%20(GPS)&userUnit11=%20'
                 '&userShortName11=Throttle'
                 '&userFullName11=Throttle%20Position(Manifold)'
                 '&userUnit0e=&deg&userShortName0e=Timing%20Adv'
                 '&userFullName0e=Timing%20Advance&userUnitff1204=miles'
                 '&userShortNameff1204=Trip&userFullNameff1204=Trip%20Distance'
                 '&userUnitff1202=psi&userShortNameff1202=Boost'
                 '&userFullNameff1202=Turbo%20Boost%20%20%20Vacuum%20Gauge').format(TestConfig.TORQUE_EMAIL)

TORQUE_READING = ('/api/torque?eml={}'
                  '&v=8&session=1463186875158'
                  '&id=alkdjfgreblrehjakefbad;f&time=1463187167064'
                  '&kff1005=-85.25377583333332&kff1006=35.13060983333333'
                  '&kff1001=0.0055559995&kff1007=0.0&k4=0.78431374'
                  '&kc=870.0&kf=21.0&k10=2.87&kff1001=0.0055559995'
                  '&k11=9.803922&ke=5.0&kff1204=3.1529496&kff1202=-12.511296').format(TestConfig.TORQUE_EMAIL)


class APITest(TestCase):
    @classmethod
    def setUpClass(self):
        os.system('influxd > /dev/null 2>&1')

    def create_app(self):
        application = ca(config=TestConfig)
        return application

    def open_with_auth(self, url, method):
        return self.client.open(url,
            method=method,
            headers={
                'Authorization': 'Basic ' + base64.b64encode(self.app.config['API_KEY'] + \
                ":")
            }
        )

    def test_api_rejects_unauthorized(self):
        self.assert401(self.client.get('/api/'))
        self.assert401(self.client.get('/api/torque'))

    def test_api_accepts_authorized(self):
        self.assert200(self.open_with_auth('/api/', method='GET'))

        params = {'eml':urllib.quote(self.app.config['TORQUE_EMAIL'])}
        response = self.client.get('/api/torque', query_string=params)

        # Cannot expect 200 because other params are missing
        self.assertNotEqual(response.status, 401)

    def test_torque_session_start(self):
        # test that it doesn't break -- no functionality test yet
        response = self.client.get(SESSION_START)
        self.assertEqual(response.data, 'OK!')

    def test_torque_reading(self):
        # test that it doesn't break -- no functionality test yet
        response = self.client.get(TORQUE_READING)
        self.assertEqual(response.data, 'OK!')


if __name__ == '__main__':
    unittest.main()
