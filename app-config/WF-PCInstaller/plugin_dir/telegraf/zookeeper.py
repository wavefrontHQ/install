"""
Tested with zookeeper 3.4.8 (Ubuntu 14.04)
"""
import common.install_utils as utils
import plugin_dir.plugin_installer as inst
import common.config as config
import plugin_dir.utils.plugin_utils as p_utils
import plugin_dir.telegraf.telegraf_utils as tf_utils


class ZookeeperConfigurator(inst.PluginInstaller):
    def title(self):
        utils.cprint(
    '__________             __                                       \n'
    '\____    /____   ____ |  | __ ____   ____ ______   ___________  \n'
    '  /     //  _ \ /  _ \|  |/ // __ \_/ __ \\\\____ \_/ __ \_  __ \ \n'
    ' /     /(  <_> |  <_> )    <\  ___/\  ___/|  |_> >  ___/|  | \/ \n'
    '/_______ \____/ \____/|__|_ \\\\___  >\___  >   __/ \___  >__|    \n'
    '        \/                 \/    \/     \/|__|        \/        \n')

    def overview(self):
        utils.cprint()
        utils.cprint(
            'The zookeeper plugin collect statistics from\n'
            'a Zookeeper server using the mntr command.\n'
            'The mntr command requires Zookeeper 3.4.0+.\n'
            'To enable zookeeper plugin,\n'
            'We need the hostname and the port to connect\n'
            'to the zookeeper server.\n')

        _ = utils.cinput('Press Enter to continue')
        utils.print_step('Begin telegraf Zookeeper plugin installer')

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
            (host, port) = p_utils.get_host_and_port(def_port='2181')
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
        utils.print_step('Begin writing telegraf zookeeper configuration')
        server_list = data['servers']
        count = len(server_list)
        if not count:
            return False

        conf = tf_utils.get_sample_config('zookeeper')
        if conf is None:
            raise Exception(
                'Cannot obtain sample config with telegraf command')

        server_list_str = p_utils.json_dumps(server_list)

        res = tf_utils.edit_conf(
            conf, 'servers', server_list_str)

        out.write(res)
        return True

if __name__ == '__main__':
    zk = ZookeeperConfigurator(
        'DEBIAN', 'TELEGRAF', 'zookeeper', 'wavefront_zookeeper.conf')
    config.INSTALL_LOG = '/dev/stdout'
    zk.install()
