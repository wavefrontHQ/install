"""
Tested with Apache/2.4.7 (Ubuntu 14.04)
"""
import common.config as config
import plugin_dir.collectd.apache as p_inst
import plugin_dir.plugin_installer_test as t_inst


class ApacheConfiguratorTest(
        t_inst.PluginInstallerTest, p_inst.ApacheConfigurator):
    def collect_data(self):
        """
        data = {
            "instance_name": "url",
        }
        """
        data = {
            "docker_test": "http://localhost/server-status"
        }
        return data
 

if __name__ == '__main__':
    apache = ApacheConfiguratorTest(
        'DEBIAN', 'COLLECTD', 'apache', 'test_wavefront_apache.conf')
    config.INSTALL_LOG = '/dev/stdout'
    apache.install()
