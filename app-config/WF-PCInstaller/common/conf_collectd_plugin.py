import sys

import common.install_utils as utils
import common.config as config


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
    res = utils.check_path_exists(config.COLLECTD_HOME)
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
    res = utils.check_path_exists(config.COLLECTD_CONF_DIR)
    if not res:
        utils.cprint('Creating collectd managed config dir')
        utils.call_command('mkdir ' + config.COLLECTD_CONF_DIR)


if __name__ == '__main__':
    utils.print_warn('This is for testing conf_collected_plugin.py')
    utils.cprint(config.COLLECTD_HOME)
    utils.cprint(config.COLLECTD_CONF_DIR)
