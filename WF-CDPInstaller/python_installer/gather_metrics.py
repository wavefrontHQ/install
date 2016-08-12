#!/usr/bin/env python
"""
The main module file that will be invoked by the one line installer.

Usage: gather_metrics [operating system(DEBIAN|REDHAT)] log file]

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

import common.conf_collectd_plugin as conf
import common.install_utils as utils
import common.config as config

# Python required base version
REQ_VERSION = (2, 7)
# Install state of app
INCOMPLETE = 2
NEW = 1
INSTALLED = 0


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


def check_app(output, app_dict):
    """
    return true if the app exists

    checks if the keyword from support_plugins can be matched
    in ps -ef output.
    if not, check if the command matches
    """
    app_search = app_dict['app_search']
    app_cmds = app_dict['command'].split('|')

#    app_re = re.search(
#        r' ({app_search})\n'.format(
#            app_search=app_search), output.decode())

    for line in output.decode().split('\n'):
        app_re = re.search(
            r'({app_search})'.format(
                app_search=app_search), line)
        if app_re is not None:
            if config.DEBUG:
                utils.eprint(line)
            return True

    if app_re is None:
        for cmd in app_cmds:
            if config.DEBUG:
                utils.eprint('Command: {}'.format(cmd))
            if cmd == "None":
                return False
            elif utils.command_exists(cmd):
                return True
        return False

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
    apache, cassandra, mysql, nginx, postgresql
    This function uses unix command ps -ef and check whether
    the supported application is found.
    """

    if config.DEBUG:
        plugins_file = config.PLUGINS_FILE
    else:
        plugins_file = '{}/{}'.format(config.APP_DIR, config.PLUGINS_FILE)
    utils.print_step('Begin app detection')

    res = utils.get_command_output('ps -ef')
    if res is None:
        utils.exit_with_message('Unable to read process off the machine')

    try:
        data_file = open(plugins_file)
    except (IOError, OSError) as e:
        utils.exit_with_message(e)
    except Exception as e:
        utils.exit_with_message('Unexpected error: {}.'.format(e))

    try:
        data = json.load(data_file)
    finally:
        data_file.close()

    support_dict = collections.OrderedDict(data['data'])
    support_list = []

    for app in support_dict:
        app_dict = support_dict[app]
        if check_app(res, app_dict):
            support_list.append(app)

    if len(support_list):
        return (support_list, support_dict)
    else:
        utils.cprint('No supported app plugin is detected')
        sys.exit(0)


def installer_menu(app_list, support_dict):
    """
    provide the menu and prompts for the user to interact with the installer

    installer flow:
      1. show selections
      2. installs a plugin
      3. updates install state (not yet implemented)
      4. menu changes with install state (not yet implemented)

    Option  Name                 State      Date
    (1)     mysql Installer      Installed  (installation date)
    (2)     apache Installer     Incomplete
    (3)     postgres Installer   New

    if resinstall,
      warn that this will overwrite {conf_file}.
    """
    exit_cmd = [
        'quit', 'q', 'exit']
    count = 0

    # the format of each row in installing menu
    menu_rowf = (
        '{index:{index_pad}} {name:{name_pad}} '
        '{state:{state_pad}} {date}')
    index_pad = 7
    name_pad = 30
    state_pad = 12
    color = utils.BLACK  # default

    res = None  # to begin the prompt loop
    utils.cprint()
    utils.cprint(
        'We have detected the following applications that are '
        'supported by our collectd installers.')

    while res not in exit_cmd:
        utils.cprint()
        utils.cprint(
            'The following are the available installers:')

        utils.cprint(
            menu_rowf.format(
                index='Option', index_pad=index_pad,
                name='Name', name_pad=name_pad,
                state='State', state_pad=state_pad,
                date='Date'))

        install_state = check_install_state(app_list)
        for i, app in enumerate(app_list):
            index = '({i})'.format(i=i)
            app_installer = '{} installer'.format(app)
            app_state = install_state[app]['state']
            if 'date' in install_state[app]:
                date = install_state[app]['date']
            else:
                date = ''

            if app_state == NEW:
                state = 'New'
                color = utils.GREEN
            elif app_state == INCOMPLETE:
                state = 'Incomplete'
                color = utils.YELLOW
            elif app_state == INSTALLED:
                state = 'Installed'
                color = utils.BLACK

            utils.print_color_msg(
                menu_rowf.format(
                    index=index, index_pad=index_pad,
                    name=app_installer, name_pad=name_pad,
                    state=state, state_pad=state_pad,
                    date=date), color)
        utils.cprint()
        utils.cprint(
            'To pick a installer, type in the corresponding number '
            'next to the installer.\n'
            'To quit out of this installer, type "[Q]uit" or "exit".')
        res = utils.get_input(
            'Which installer would you like to run?').lower()
        if res not in exit_cmd:
            option = check_option(res, len(app_list))
            if option is not None:
                app = support_dict[app_list[option]]
                utils.cprint(
                    'You have selected ({option}) {app} installer'.format(
                        option=option, app=app_list[option]))
                app_state = install_state[app_list[option]]['state']
                if app_state == INSTALLED:
                    utils.print_warn(
                        'You have previously used this installer\n'
                        'Reinstalling will overwrite the old configuration '
                        'file, {}.'.format(app['conf_name']))
                confirm = utils.ask(
                    'Would you like to proceed with '
                    'the installer?')
                if confirm:
                    Installer = getattr(
                        importlib.import_module(
                            '{direc}.{mod}'.format(
                                direc='plugin_dir',
                                mod=app['module'])),
                        app['class_name'])
                    instance = Installer(
                        config.OPERATING_SYSTEM,
                        app['plugin_name'],
                        app['conf_name'])
                    if instance.install():
                        install_state[app_list[option]]['state'] = INSTALLED
                        count += 1
                    else:
                        install_state[app_list[option]]['state'] = INCOMPLETE
                    install_state[app_list[option]]['date'] = '{:%c}'.format(
                        datetime.now())
                    update_install_state(install_state)
            else:
                utils.print_reminder('Invalid option.')
    return count


def check_install_state(app_list):
    """
    Given: a list of app name
    return: a list of app_name and their states

    Flow:
     - check file path exists
     - if exists:
           check each app against the fiel
           keep track of app and their states
    """
    file_not_found = False
    empty_state_dict = {}
    for app in app_list:
        empty_state_dict[app] = {}
        empty_state_dict[app]['state'] = NEW

    if config.DEBUG:
        file_path = config.INSTALL_STATE_FILE
    else:
        file_path = config.INSTALL_STATE_FILE_PATH
    file_not_found = not utils.check_path_exists(file_path)

    try:
        install_file = open(file_path)
    except (IOError, OSError) as e:
        file_not_found = True
    except Exception as e:
        utils.exit_with_message('Error: {}'.format(e))

    if file_not_found:
        return empty_state_dict

    try:
        data = json.load(install_file)
    finally:
        install_file.close()
    data = data['data']
    for app in app_list:
        if app not in data:
            data[app] = {}
            data[app]['state'] = NEW
    return data


def update_install_state(app_state_dict):
    comment = {
          "standard_format": "see below",
          "APP_NAME": {
              "state": "(INSTALLED = 0, INCOMPLETE = 1, NEW = 2)",
              "date": "time_of_installation"
          }
      }
    json_content = collections.OrderedDict()
    json_content['_comment'] = comment
    json_content.update({'data': app_state_dict})

    # TODO: needs to find a path to save this file
    file_path = config.INSTALL_STATE_FILE_PATH

    try:
        outfile = open(file_path, 'w')
    except:
        utils.eprint(
            'Cannot write to {}.\n'
            'Installed state is not updated.'.format(file_path))
        outfile = None

    if outfile is not None:
        try:
            json.dump(json_content, outfile, indent=4)
        finally:
            outfile.close()


def check_option(option, max_length):
    """
    check if option is a num or if it is out of range
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
    arg_len = len(sys.argv)
    if arg_len == 3:
        config.OPERATING_SYSTEM = sys.argv[1]
        config.INSTALL_LOG = sys.argv[2]
    elif arg_len == 1:
        config.INSTALL_LOG = '/dev/null'
    else:
        utils.eprint('Invalid arguments.')
        sys.exit(1)

    if config.DEBUG:
        utils.print_warn('DEBUG IS ON')

    (s_list, s_dict) = detect_applications()

    try:
        if installer_menu(s_list, s_dict):
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        utils.eprint('\nQuitting the installer via keyboard interrupt.')
        sys.exit(1)
