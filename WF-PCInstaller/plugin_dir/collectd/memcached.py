"""
memcached 1.4.14 (Ubuntu 14.04)
"""
import common.install_utils as utils
import common.config as config
import plugin_dir.plugin_installer as inst
import plugin_dir.utils.plugin_utils as p_utils


class MemcachedConfigurator(inst.PluginInstaller):
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

    def collect_data(self):
        """
        data = {
            instance_name: {
                host: value
                port: value
            }
        }
        """
        data = {}
        iname_list = []
        server_list = []

        while utils.ask('\nWould you like to add a server to monitor?'):
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

            (host, port) = p_utils.get_host_and_port(def_port='11211')

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
                iname_list.append(iname)
                server_list.append((host, port))
                data[iname] = {
                    "host": host,
                    "port": port
                }
                utils.print_success()
            else:
                utils.cprint('This instance is not saved.')

        return data

    def output_config(self, data, out):
        utils.print_step('Begin writing memcached plugin for collectd')
        if not data:
            return False

        out.write('LoadPlugin "memcached"\n')
        out.write('<Plugin "memcached">\n')

        for instance in data:
            out.write(
                '  <Instance "{iname}">\n'
                '    Host "{host}"\n'
                '    Port "{port}"\n'
                '  </Instance>\n'.format(
                    iname=instance,
                    host=data[instance]['host'],
                    port=data[instance]['port']))

        out.write('</Plugin>\n')
        return True

if __name__ == '__main__':
    mc = MemcachedInstaller(
        'DEBIAN', 'memcached', 'wavefront_memcached.conf')
    config.INSTALL_LOG = '/dev/stdout'
    mc.install()
