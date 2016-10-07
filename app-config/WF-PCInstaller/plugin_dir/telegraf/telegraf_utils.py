import re

import common.install_utils as utils
import common.config as config


def get_sample_config(name):
    """
    using telegraf command to generate the plugin config

    Input:
        name string:
            the name of plugin
    Output:
        returns the output of the following command
        telegraf -usage name
    """
    command = (
        'telegraf -usage {name}'.format(name=name))
    return utils.get_command_output(command)


def edit_conf(conf, key, value):
    """
    read the sample config and modify the appropriate field

    Input:
        key string
            - the key field in the conf
        value string
            - the corresponding key value
    Output:
        res_conf string
            - the configuration string with the
              proper field changed

    use regex substitute key = (old value)
    with the supplied key = value
    """

    # regex search for key
    search_re = re.compile(
        r'{key} = '.format(key=key), re.I)

    # break the conf by new line since the telegraf
    # conf has key = value format per line
    conf_list = conf.split('\n')
    for index, line in enumerate(conf_list):
        search_res = search_re.search(line)
        if search_res is not None:
            conf_list[index] = (
                re.sub(
                    r'{key} = .*'.format(key=key),
                    '{key} = {value}'.format(key=key, value=value),
                    line))

    # make sure new line is reinserted
    res_conf = '\n'.join(conf_list)
    if config.DEBUG:
        utils.cprint('After change:')
        utils.cprint(res_conf)

    return res_conf


if __name__ == '__main__':
    utils.print_step('Testing module {}'.format(__loader__.fullname))
    utils.cprint(get_sample_config('apache'))
