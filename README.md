# torque_server
Put your [torque-app](https://torque-bhp.com/) data into [influxdb](https://influxdata.com/time-series-platform/influxdb/).

## Environment Variables:
* `$ cp .env.example .env`
* Modify `.env` to suit your needs
* App environment variables are loaded in `./app/config.py`.
* Deployment environment variables are uses in `./deploy/fabfile.py`

## Installation/Deployment:
My servers run Ubuntu 14.04, so that's what I have setup deployment for.

* Take care of your environment variables.
* `$ cd deploy`
* `$ fab production setup_ubuntu_1404` ... This will reboot your server
* `$ fab production deploy`
* `$ fab production update_env_vars`

## Streaming Torque Data
* Point your torque app to `http(s)://your_server_address/api/torque`
* From my small amount of snooping with the torque app requests, there
are two basic types of requests
  * Session Start -- Includes friendly names of measurements, units, and a session id
  * Torque Reading -- Key/value pairs with non-human readable keys that must be decoded from the app PIDs or the Session Start data.
  * These are translated into `session_start` and `torque_reading` measurements in influx.

## A note about security
As I was investigating the torque app's api requests, it seems that the app will strip out any added query parameters or basic auth credentials from the data logging url.  However, as a user, you may enter your "email" into the torque app, and whatever you place here will be passed as a query parameter.  This is the parameter checked for authentication. As far as I know, there are no restrictions on what you can fill in for the user email, field, so I would model my entry after a secure api key and set the `TORQUE_EMAIL` env var to match.

The `API_KEY` env var is used to protect the (non-existent) remainder of the api.
