"""
mysql  Ver 14.14 Distrib 5.5.49 (Ubuntu 14.04)
"""
import common.config as config
import plugin_dir.plugin_installer_test as t_inst
import plugin_dir.collectd.mysql as p_inst


class MySQLConfiguratorTest(
        t_inst.PluginInstallerTest, p_inst.MySQLConfigurator):

    def collect_data(self):
        """
        Prompt the user for information, and guide them through the plugin

        data = {
            "db": {
                "username": username,
                "password": password,
                "host": host,
                "port or socket":
            }
        }
        """
        data = {
            "docker_test": {
                'username': 'docker',
                'password': 'docker',
                'host': 'localhost',
                'port': '3306'
            }
        }

        return data


if __name__ == '__main__':
    sql = MySQLConfiguratorTest(
        'DEBIAN', 'COLLECTD', 'mysql', 'test_wavefront_mysql.conf')
    config.INSTALL_LOG = '/dev/stdout'
    sql.install()
