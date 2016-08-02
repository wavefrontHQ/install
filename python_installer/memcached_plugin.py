import re

import install_utils as utils
import plugin_installer as inst
import config


class MemcachedInstaller(inst.PluginInstaller):
    def title(self):
        utils.cprint(
    ' __  __                                     _                _ \n'
    '|  \/  |                                   | |              | |\n'
    '| \  / |  ___  _ __ ___    ___  __ _   ___ | |__    ___   __| |\n'
    '| |\/| | / _ \| \'_ ` _ \  / __|/ _` | / __|| \'_ \  / _ \ /   `|\n'
    '| |  | ||  __/| | | | | || (__| (_| || (__ | | | ||  __/| (_| |\n'
    '|_|  |_| \___||_| |_| |_| \___|\__,_| \___||_| |_| \___| \__,_|\n')

    def overview(self):
        utils.cprint()
        utils.cprint(
            'The memcached plugin connects to a memcached server\n'
            'and queries statistics about cache utilization,\n'
            'memory and bandwidth used.\n\n'
            'To enable collectd memcached plugin,\n'
            'We just need the hostname and the port to connect\n'
            'to the memcached server.\n')

        _ = utils.cinput('Press Enter to continue')
        utils.print_step('Begin collectd Memcached plugin installer')

    def check_dependency(self):
        pass

    def write_plugin(self, out):
        count = 0  # number of server being monitored
        iname_list = []
        server_list = []

        utils.print_step('Begin writing memcached plugin for collectd')
        out.write('LoadPlugin "memcached"\n')
        out.write('<Plugin "memcached">\n')

        while utils.ask('Would you like to add a server to monitor?'):
            iname = utils.prompt_and_check_input(
                prompt=(
                    '\nHow would you like to name this monitoring instance?\n'
                    '(How it should appear on your wavefront metric page, \n'
                    'space between words will be removed)'),
                check_func=(
                    lambda x: x.replace(" ", "") not in iname_list),
                usage=(
                    '{} has already been used.'.format),
                usage_fmt=True).replace(" ", "")

            host = utils.prompt_and_check_input(
                prompt=(
                    'Please enter the hostname that connects to your\n'
                    'memcached server:'),
                check_func=utils.hostname_resolves,
                usage='{} does not resolve.'.format,
                usage_fmt=True,
                default='127.0.0.1')

            port = utils.prompt_and_check_input(
                prompt=(
                    'What is the TCP-port used to connect to the host? '),
                check_func=utils.check_valid_port,
                usage=(
                    'A valid port is a number '
                    'between (0, 65535) inclusive.\n'),
                default='11211')

            if (host, port) in server_list:
                utils.eprint(
                    'You have already added this {host}:{port}.'.format(
                        host=host, port=port))
                continue

            plugin_instance = (
                '  <Instance "{iname}">\n'
                '    Host "{host}"\n'
                '    Port "{port}"\n'
                '  </Instance>\n').format(
                    iname=iname,
                    host=host, port=port)

            utils.cprint()
            utils.cprint('Result: \n{}'.format(plugin_instance))
            res = utils.ask('Is the above information correct?')

            if res:
                utils.print_step('Saving instance')
                count = count + 1
                iname_list.append(iname)
                server_list.append((host, port))
                out.write(plugin_instance)
                utils.print_success()
            else:
                utils.cprint('This instance is not saved.')
        out.write('</Plugin>\n')
        return count

if __name__ == '__main__':
    mc = MemcachedInstaller(
        'DEBIAN', 'memcached', 'wavefront_memcached.conf')
    config.INSTALL_LOG = '/dev/null'
    mc.install()
