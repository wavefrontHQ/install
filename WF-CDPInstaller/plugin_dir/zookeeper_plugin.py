import install_utils as utils
import plugin_installer as inst
import config


class ZookeeperInstaller(inst.PluginInstaller):
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

    def write_plugin(self, out):
        count = 0  # number of server being monitored

        utils.print_step('Begin writing zookeeper plugin for collectd')
        out.write('LoadPlugin "zookeeper"\n')
        out.write('<Plugin "zookeeper">\n')

        while count == 0:  # can only monitor one for this plugin
            host = utils.prompt_and_check_input(
                prompt=(
                    'Please enter the hostname that connects to your\n'
                    'zookeeper server:\n'
                    '(This plugin can only monitor one server)'),
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
                default='2181')

            plugin_instance = (
                '    Host "{host}"\n'
                '    Port "{port}"\n').format(
                    host=host, port=port)

            utils.cprint()
            utils.cprint('Result: \n{}'.format(plugin_instance))
            res = utils.ask('Is the above information correct?')

            if res:
                utils.print_step('Saving instance')
                count = count + 1
                out.write(plugin_instance)
                utils.print_success()
            else:
                utils.cprint('This instance is not saved.')
                utils.cprint()
        out.write('</Plugin>\n')
        return count

if __name__ == '__main__':
    zk = ZookeeperInstaller(
        'DEBIAN', 'zookeeper', 'wavefront_zookeeper.conf')
    config.INSTALL_LOG = '/dev/null'
    zk.install()
