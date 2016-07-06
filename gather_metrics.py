import socket
import sys
import getopt
from datetime import datetime
import subprocess

import conf_collectd_plugin as conf
import install_utils as utils
import config

# Python required base version, haven't tested 3 yet.
REQ_VERSION = (2, 7)


def check_version():
    cur_version = sys.version_info
    utils.print_step("  Checking python version")
    if cur_version < REQ_VERSION:
        sys.stderr.write(
            "Your Python interpreter is older " +
            "than what we have tested, we suggest upgrading " +
            "to a newer 2.7 version before continuing.\n")
        sys.exit()
    utils.print_success()


def port_scan(host, port):
    """
    Using ipv4, TCP connection to test whether a port is
    being used.
    """
    # AF_INET specifies ipv4, SOCK_STREAM for TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((host, port))
    except socket.error:
        return False
    except KeyboardInterrupt:
        print "Scanning interrupted"
        sys.exit()
    except socket.gaierror:
        print "Hostname could not be resolved"
        sys.exit()
    else:
        return port
    finally:
        sock.close()


def detect_used_ports():
    """
    Scan through localhost 0-1024 ports
    """
    MAX_PORT = 1025
    DEFAULT_HOST = '127.0.0.1'
    open_ports = []
    socket.setdefaulttimeout(1)
    for port in range(0, MAX_PORT):
        res = port_scan(DEFAULT_HOST, port)
        if(res is not False):
            open_ports.append(port)
        # debugging purpose to see if program is running
        if(port % 5000 == 0 and port != 0):
            sys.stderr.write(".")
    return open_ports


def detect_applications():
    """
    Current collectd plugin support:
    apache.
    Want: nginx, sql, postgres, amcq
    This function uses unix command ps -A and check whether
    the supported application is listed.
    """

    try:
        res = subprocess.check_output(
            'ps -A', shell=True,
            stderr=subprocess.STDOUT,
            executable='/bin/bash')
    except:
        print "Unexpected error."
        sys.exit(1)

    if 'apache' in res or 'httpd' in res:
        conf.install_apache_plugin()
    if 'nginx' in res:
        print "Has nginx"
    if 'sql' in res:
        print "Has sql"
    if 'postgres' in res:
        print "Has postgres"
    if 'AMCQ' in res:
        print "Has AMCQ"


if __name__ == "__main__":
    check_version()
    conf.check_collectd_exists()
    conf.check_collectd_path()

    if len(sys.argv) > 1:
        config.INSTALL_LOG = sys.argv[1]
    else:
        config.INSTALL_LOG = "/dev/null"

    try:
        conf.print_log()
        detect_applications()
    except KeyboardInterrupt:
        sys.stderr.write("\nQuitting the installer via keyboard interrupt.")
        sys.exit(1)
