"""
zookeeper 3.4.8 (Ubuntu 14.04)
"""
import common.install_utils as utils
import plugin_dir.plugin_installer as inst
import plugin_dir.utils.plugin_utils as p_utils
import common.config as config


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
            'The collectd zookeeper plugin collect statistics from\n'
            'a Zookeeper server using the mntr command.\n'
            'The mntr command requires Zookeeper 3.4.0+.\n'
            'To enable collectd zookeeper plugin,\n'
            'We need the hostname and the port to connect\n'
            'to the zookeeper server.\n')

        _ = utils.cinput('Press Enter to continue')
        utils.print_step('Begin collectd Zookeeper plugin installer')

    def check_dependency(self):
        pass

    def collect_data(self):
        """
        note: can only monitor one instance
        """
        data = {}
        record = True
        while record:
            (host, port) = p_utils.get_host_and_port(def_port='2181')
            plugin_instance = (
                '    Host "{host}"\n'
                '    Port "{port}"\n').format(
                    host=host, port=port)

            utils.cprint()
            utils.cprint('Result: \n{}'.format(plugin_instance))
            res = utils.ask('Is the above information correct?')

            if res:
                utils.print_step('Saving instance')
                record = False
                data = {
                    'host': host,
                    'port': port
                }
                utils.print_success()
            else:
                utils.cprint('This instance is not saved.')

        return data

    def output_config(self, data, out):
        utils.print_step('Begin writing zookeeper plugin for collectd')
        out.write(
            'LoadPlugin "zookeeper"\n'
            '<Plugin "zookeeper">\n'
            '    Host "{host}"\n'
            '    Port "{port}"\n'
            '</Plugin>\n'.format(
                host=data['host'],
                port=data['port']))
        return True

if __name__ == '__main__':
    zk = ZookeeperConfigurator(
        'DEBIAN', 'COLLECTD', 'zookeeper', 'wavefront_zookeeper.conf')
    config.INSTALL_LOG = '/dev/stdout'
    zk.install()
