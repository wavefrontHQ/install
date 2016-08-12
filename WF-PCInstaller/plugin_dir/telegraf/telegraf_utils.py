import re

import common.install_utils as utils
import common.config as config


def get_sample_config(name):
    """
    using telegraf command to generate the plugin config
    
    returns the output of the following command
        telegraf -usage name
    """
    command = (
        'telegraf -usage {name}'.format(name=name))
    return utils.get_command_output(command)


if __name__ == '__main__':
    utils.print_step('Testing module {}'.format(__name__))
    utils.cprint(get_sample_config('apache'))
