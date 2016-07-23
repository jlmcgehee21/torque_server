import os
from fabric.api import run, cd, env, lcd, sudo, put, local, settings, hosts, execute, prefix


CURDIR = os.path.dirname(os.path.realpath(__file__))

local_app_dir = os.path.join(os.path.dirname(CURDIR))
remote_app_dir = '/var/www/torque_server'
app_name = 'torque_server'

service_names = ['torque_influx',
                 'torque_server']


def production():
    env.user = os.getenv('PRODUCTION_USER', '')
    env.password = os.getenv('PRODUCTION_PASS', '')
    env.hosts = [os.getenv('PRODUCTION_URL', '')]

# Services
def stop_all_services():
    with settings(warn_only=True):
        # Stop our processes if they're running
        for service in service_names:
            sudo('service %s stop'%(service))


def start_all_services():
    with settings(warn_only=True):
        # Stop our processes if they're running
        for service in service_names:
            sudo('service %s start'%(service), shell=False)

def update_service_conf():
    for service in service_names:
        try:
            put('%s.conf'%(service), '/etc/init', use_sudo=True)
        except ValueError:
            print 'No conf file for %s'%service

def update_env_vars():
    stop_all_services()

    with lcd(local_app_dir):
        with cd(remote_app_dir):
            put('.env', './')

    start_all_services()

def check_service_logs():
    with settings(warn_only=True):
        for service in service_names:
            sudo('tail -n 100 /var/log/upstart/%s.log'%(service))

        sudo('tail -n 100 /var/www/torque_server/app/logs/uwsgi.log')


def clear_service_logs():
    with settings(warn_only=True):
        for service in service_names:
            sudo('> /var/log/upstart/%s.log'%(service))

# Deploy
def deploy():
    stop_all_services()
    clear_service_logs()

    with lcd(local_app_dir):
        local('find . -type f -name \'*.pyc\' -delete')
        sudo('mkdir -p %s' % (remote_app_dir))
        sudo('chown %s %s'%(env.user, remote_app_dir))
        with cd(remote_app_dir):
            put('*', './')
            run('mkdir -p app/logs')
            run('touch app/logs/uwsgi.log')
            # create virtualenv with the system packages (scipy)
            sudo('virtualenv env --system-site-packages')
            sudo('env/bin/pip install -r requirements.txt')

    update_service_conf()
    start_all_services()

def install_python_basic():
    sudo('apt-get -y install python-dev build-essential')
    sudo('apt-get -y install python-pip')
    sudo('pip install virtualenv')

def install_git():
    sudo('apt-get -y install git-all')

def install_influxdb():
    sudo('curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -')
    sudo('source /etc/lsb-release')
    sudo('echo "deb https://repos.influxdata.com/ubuntu trusty stable" | sudo tee /etc/apt/sources.list.d/influxdb.list')
    sudo('apt-get update')
    sudo('apt-get -y install influxdb')

def install_uwsgi():
    sudo('apt-get -y install uwsgi')
    sudo('apt-get -y install uwsgi-plugin-python')

def setup_ubuntu_1404():
    sudo('apt-get update')

    # Python
    install_python_basic()

    # Influx
    install_influxdb()

    install_uwsgi()

    # need git for pip installs from git repos
    install_git()

    sudo('reboot')


if __name__ == "__main__":
    pass
