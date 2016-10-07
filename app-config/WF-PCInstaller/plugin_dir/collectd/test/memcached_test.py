"""
memcached 1.4.14 (Ubuntu 14.04)
"""
import common.config as config
import plugin_dir.plugin_installer_test as t_inst
import plugin_dir.collectd.memcached as p_inst


class MemcachedConfiguratorTest(
        t_inst.PluginInstallerTest, p_inst.MemcachedConfigurator):

    def collect_data(self):
        """
        data = {
            instance_name: {
                host: value
                port: value
            }
        }
        """
        data = {
            'docker_test': {
                'host': 'localhost',
                'port': '11211'
            }
        }

        return data


if __name__ == '__main__':
    mc = MemcachedInstaller(
        'DEBIAN', 'COLLECTD', 'memcached', 'wavefront_memcached.conf')
    config.INSTALL_LOG = '/dev/stdout'
    mc.install()
