import sys
import re

import install_utils as utils
import config

COLLECTD_HOME = '/etc/collectd'
COLLECTD_CONF_DIR = COLLECTD_HOME + '/managed_config'

# http response header
NOT_AUTH = 401
NOT_FOUND = 404
HTTP_OK = 200
INVALID_URL = -1


def check_collectd_exists():
    utils.print_step('  Checking if collectd exists')
    if not utils.command_exists('collectd'):
        sys.stderr.write(
            'Collectd is not installed.\n'
            'Please rerun the installer with --collectd option.\n')
        sys.exit(1)
    utils.print_success()


def check_collectd_path():
    utils.print_step(
        '  Checking if collectd is installed in our specified '
        'directory')
    res = utils.check_path_exists(COLLECTD_HOME)
    if not res:
        sys.stderr.write(
            'Collectd was not found at our '
            'default installation folder. '
            'If you need help with configuration, please '
            'contact support@wavefront.com\n')
        sys.exit(1)
    utils.print_success()


def check_collectd_conf_dir():
    """
    Check if managed_config directory exists, if not,
    create one.
    """
    res = utils.check_path_exists(COLLECTD_CONF_DIR)
    if not res:
        utils.cprint('Creating collectd managed config dir')
        utils.call_command('mkdir ' + COLLECTD_CONF_DIR)


def check_install_state(plugin):
    utils.cprint('Cannot check install state yet.')
    return False


def write_tcpconns_conf_plugin(open_ports):
    """
    TODO:
    -need to check if tcpconn plugin's dependencies are installed
    -include RemotePort for outbounds connections
        i.e. the servers we are connecting to
    """
    try:
        out = open('10-tcpconns.conf', 'w')
    except IOError:
        sys.stderr.write('Unable to open tcpcons.conf file\n')
        sys.exit(1)
    except:
        sys.stderr.write(
            'Unexpected error.  Unable to write tcpcons.conf file\n')
        sys.exit(1)

    tcp_plugin_bef = (
        'LoadPlugin tcpconns\n'
        '<Plugin "tcpconns">\n'
        '  ListeningPorts false\n')

    out.write(tcp_plugin_bef)
    for port in open_ports:
        out.write('  LocalPort "%d"\n' % port)
    # no remote port yet
    out.write('</Plugin>\n')
    out.close()


if __name__ == '__main__':
    utils.print_warn('This is for testing conf_collected_plugin.py')
    utils.cprint(COLLECTD_HOME)
    utils.cprint(COLLECTD_CONF_DIR)
