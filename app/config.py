import os


class DefaultConfig(object):
    INFLUXDB_HOST = os.getenv('INFLUXDB_HOST', 'localhost')
    INFLUXDB_PORT = os.getenv('INFLUXDB_PORT', 8086)
    INFLUXDB_USER = os.getenv('INFLUXDB_USER', 'root')
    INFLUXDB_PASSWORD = os.getenv('INFLUXDB_PASSWORD', 'root')

    INFLUXDB_DATABASE = os.getenv('INFLUXDB_DATABASE', 'volvo_t5')

    API_KEY = os.environ['API_KEY']
    TORQUE_EMAIL = os.environ['TORQUE_EMAIL']

class TestConfig(object):
    INFLUXDB_HOST = os.getenv('INFLUXDB_TEST_HOST', 'localhost')
    INFLUXDB_PORT = os.getenv('INFLUXDB_TEST_PORT', 8086)
    INFLUXDB_USER = os.getenv('INFLUXDB_TEST_USER', 'root')
    INFLUXDB_PASSWORD = os.getenv('INFLUXDB_TEST_PASSWORD', 'root')

    INFLUXDB_DATABASE = os.getenv('INFLUXDB_TEST_DATABASE', 'test_db')

    API_KEY = os.getenv('TEST_API_KEY', 'test_key')
    TORQUE_EMAIL = os.getenv('TEST_TORQUE_EMAIL',
                              'testy_mctesterson@gmail.com')

    TESTING = True
    LIVESERVER_PORT = 8943
