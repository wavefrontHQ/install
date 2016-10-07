"""
postgresql 9.3 (Ubuntu 14.04)
"""
import common.config as config
import plugin_dir.plugin_installer_test as t_inst
import plugin_dir.collectd.postgresql as p_inst


class PostgresqlConfiguratorTest(
        t_inst.PluginInstallerTest, p_inst.PostgresqlConfigurator):
    def collect_data(self):
        """
        data = {
            instance_name: {
                db: value,
                host: value,
                port: value,
                username: value,
                password: value
            }
        }
        """
        data = {
            'docker_test': {
                'db': 'docker',
                'host': 'localhost',
                'port': '5432',
                'username': 'docker',
                'password': 'docker'
            }
        }

        return data


if __name__ == '__main__':
    postgres = PostgresqlConfiguratorTest(
        'DEBIAN', 'COLLECTD', 'postgresql', 'test_wavefront_postgres.conf')
    config.INSTALL_LOG = '/dev/stdout'
    postgres.install()
