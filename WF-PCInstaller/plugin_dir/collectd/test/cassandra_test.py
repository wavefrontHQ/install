"""
cassandra 3.7.0 (Ubuntu 14.04)
"""
import common.config as config
import plugin_dir.plugin_installer_test as t_inst
import plugin_dir.collectd.cassandra as p_inst


class CassandraConfiguratorTest(
        t_inst.PluginInstallerTest, p_inst.CassandraConfigurator):

    def collect_data(self):
        """
        data = {
            'url': url
        }
        # ServiceURL "service:jmx:rmi:///jndi/rmi://localhost:7199/jmxrmi"
        """
        data = {
            'url': 'service:jmx:rmi:///jndi/rmi://localhost:7199/jmxrmi'
        }

        return data


if __name__ == '__main__':
    cassandra = CassandraConfiguratorTest(
        'DEBIAN', 'COLLECTD', 'java', 'test_wavefront_cassandra.conf')
    config.INSTALL_LOG = '/dev/stdout'
    cassandra.install()
