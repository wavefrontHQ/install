"""
zookeeper 3.4.8 (Ubuntu 14.04)
"""
import common.config as config
import plugin_dir.plugin_installer_test as t_inst
import plugin_dir.collectd.zookeeper as p_inst


class ZookeeperConfiguratorTest(
        t_inst.PluginInstallerTest, p_inst.ZookeeperConfigurator):

    def collect_data(self):
        """
        note: can only monitor one instance
        """
        data = {
            'host': 'localhost',
            'port': '2181'
        }

        return data


if __name__ == '__main__':
    zk = ZookeeperConfiguratorTest(
        'DEBIAN', 'COLLECTD', 'zookeeper', 'test_wavefront_zookeeper.conf')
    config.INSTALL_LOG = '/dev/stdout'
    zk.install()
