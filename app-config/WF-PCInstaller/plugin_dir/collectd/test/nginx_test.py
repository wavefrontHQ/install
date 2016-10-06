"""
Tested with Nginx/1.4.6 (Ubuntu 14.04)
"""
import common.config as config
import plugin_dir.plugin_installer_test as t_inst
import plugin_dir.collectd.nginx as p_inst


class NginxConfiguratorTest(
        t_inst.PluginInstallerTest, p_inst.NginxConfigurator):

    def collect_data(self):
        """
        data = {
            url: [(list of server urls)]
        }
        """
        data = {
            'url': 'http://localhost:81/server-status'
        }

        return data


if __name__ == '__main__':
    nginx = NginxConfiguratorTest(
        'DEBIAN', 'COLLECTD', 'nginx', 'test_wavefront_nginx.conf')
    config.INSTALL_LOG = '/dev/stdout'
    nginx.install()
