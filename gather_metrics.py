#!/usr/bin/env python

"""
The main module file that will be invoked by the one line installer.

Usage: gather_metrics [optional log file]

If log file is provided, then errors will be logged to such file.
Otherwise, all errors will be flushed.

It first checks the dependency this module needs.
Detects application and calls the appropriate plugin installer.
Catches ctrl+c to prevent long error message and exit the system
with return code of 1.
"""

import socket
import sys
from datetime import datetime
import re
import importlib
import json
import collections

import conf_collectd_plugin as conf
import install_utils as utils
import config

# Python required base version
REQ_VERSION = (2, 7)

def check_version():
    cur_version = sys.version_info
    utils.print_step('  Checking python version')
    if cur_version < REQ_VERSION:
        sys.stderr.write(
            'Your Python interpreter is older '
            'than what we have tested, we suggest upgrading '
            'to a newer 2.7 version before continuing.\n')
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
        utils.cprint('Scanning interrupted')
        sys.exit()
    except socket.gaierror:
        utils.cprint('Hostname could not be resolved')
        sys.exit()
    else:
        return port
    finally:
        sock.close()


def check_app(output, app):
    app_re = re.search(r' ({app})\n'.format(app=app), output.decode())
    if config.DEBUG:
        pattern = r' ({app})\n'.format(app=app)
        utils.eprint(pattern)

    if app_re is None:
        return False
    else:
        return True

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
        if res:
            open_ports.append(port)
        # debugging purpose to see if program is running
        if port % 5000 == 0 and port != 0:
            sys.stderr.write('.')
    return open_ports


def detect_applications():
    """
    Detect and install appropriate collectd plugin

    Current collectd plugin support:
    apache, mysql.
    Want: nginx, postgres, amcq
    This function uses unix command ps -A and check whether
    the supported application is found.

    support_dict = 
      {
        'APP_NAME': 
            { APP_SEARCH: search_name,
              MODULE: module_name,
              CLASSNAME: installer_name,
              CONF_NAME: plugin_conf_filename
            }
      },

    [Q]uit to quit
    detected
      1. app1
      2. app2
      3. app3
      4. app4

    installer flow:
      1. show selections
      2. installs a plugin
      3. updates install state
      4. menu changes with install state
    """

    plugins_file = 'support_plugins.json'
    utils.eprint('Begin app detection')

    res = utils.get_command_output('ps -A')
    if res is None:
        utils.exit_with_message('Unable to read process off the machine')

    try:
        data_file = open(plugins_file)
    except (IOError, OSError) as e:
        utils.exit_with_message(e)
    except Exception:
        utils.exit_with_message('Unexpected error.')

    data = json.load(data_file)
    support_dict = collections.OrderedDict(data['data'])
    support_list = []

    for app in support_dict:
        if check_app(res, support_dict[app]['app_search']):
            support_list.append(app)
    utils.cprint(support_list) 
   

    if len(support_list):
        installer_menu(support_list, support_dict)
    else:
        utils.cprint('No supported app plugin is detected')
        sys.exit(0)

    """
    MyClass = getattr(importlib.import_module("mysql_plugin"),
        "MySQLInstaller")
    instance = MyClass('testing')
    instance.install()
    """


def installer_menu(o_list, support_dict):
    """
    """
    exit_cmd = [
        'quit', 'q', 'exit']

    res = None
    utils.cprint()
    utils.print_reminder(    
        'We have detected the following applications that are '
        'supported by our collectd installers.')

    while res not in exit_cmd:
        utils.cprint()
        utils.cprint('The following are the available installers')
        for i, app in enumerate(o_list):
            utils.cprint(
                '({i}) {app} installer'.format(i=i, app=app))
        utils.cprint()
        utils.cprint(
            'To pick a installer, type in the corresponding number '
            'next to the installer.\n'
            'To quit out of this installer, type "[Q]uit" or "exit".')
        res = utils.get_input(
            'Which installer would you like to run?').lower()
        if res not in exit_cmd:
            option = check_option(res, len(o_list))
            if option is not None:
                utils.cprint(
                    'You have selected ({option}) {app} installer'.format(
                        option=option, app=o_list[option]))
                confirm = utils.ask('Would you like to proceed with '
                    'the installer?')
                if confirm:
                    app = support_dict[o_list[option]]
                    Installer = getattr(
                        importlib.import_module(app['module']),
                        app['class_name'])
                    instance = Installer('Debian', app['conf_name'])
                    instance.install()
            else:
                utils.print_reminder('Invalid option.')

def check_option(option, max_length):
   """
   sanitize input
   check if it is out of range, num.
   """
   res = utils.string_to_num(option)
   if res is None:
      return None
       
   if res < 0 or res >= max_length:
      return None
   return res

if __name__ == '__main__':
    check_version()
    conf.check_collectd_exists()
    conf.check_collectd_path()

    # the first argument will be the log file
    if len(sys.argv) > 1:
        config.INSTALL_LOG = sys.argv[1]
    else:
        config.INSTALL_LOG = '/dev/null'

    try:
        detect_applications()
    except KeyboardInterrupt:
        sys.stderr.write('\nQuitting the installer via keyboard interrupt.')
        sys.exit(1)
