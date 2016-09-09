"""
Tested with memcached 1.4.14 (Ubuntu 14.04)
"""
import common.install_utils as utils
import common.config as config
import plugin_dir.plugin_installer as inst
import plugin_dir.utils.plugin_utils as p_utils
import plugin_dir.telegraf.telegraf_utils as tf_utils


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
            'To enable memcached plugin,\n'
            'hostname and the port are needed to connect\n'
            'to the memcached server.\n')

        _ = utils.cinput('Press Enter to continue')
        utils.print_step('Begin telegraf Memcached plugin installer')

    def check_dependency(self):
        pass

    def collect_data(self):
        """
        data = {
            servers: []
        }
        """
        data = {
            'servers': []
        }
        server_list = []

        while utils.ask('\nWould you like to add a server to monitor?'):
            (host, port) = p_utils.get_host_and_port(def_port='11211')
            if (host, port) in server_list:
                utils.eprint(
                    'You have already added this {host}:{port}.'.format(
                        host=host, port=port))
                continue

            plugin_instance = (
                '    Host "{host}"\n'
                '    Port "{port}"\n').format(
                    host=host, port=port)

            utils.cprint()
            utils.cprint('Result: \n{}'.format(plugin_instance))
            res = utils.ask('Is the above information correct?')

            if res:
                utils.print_step('Saving instance')
                server_list.append((host, port))
                data['servers'].append(
                    '{host}:{port}'.format(
                        host=host, port=port))
                utils.print_success()
            else:
                utils.cprint('This instance is not saved.')

        return data

    def output_config(self, data, out):
        utils.print_step('Begin writing telegraf memcached configuration')
        server_list = data['servers']
        count = len(server_list)
        if not count:
            return False

        conf = tf_utils.get_sample_config('memcached')
        if conf is None:
            raise Exception(
                'Cannot obtain sample config with telegraf command')

        server_list_str = p_utils.json_dumps(server_list)

        res = tf_utils.edit_conf(
            conf, 'servers', server_list_str)

        out.write(res)
        return True

if __name__ == '__main__':
    mc = MemcachedConfigurator(
        'DEBIAN', 'TELEGRAF', 'memcached', 'wavefront_memcached.conf')
    config.INSTALL_LOG = '/dev/stdout'
    mc.install()
