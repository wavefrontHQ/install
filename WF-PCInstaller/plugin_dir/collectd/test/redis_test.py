"""
redis-server 2.8.4 (Ubuntu 14.04)
"""
import common.install_utils as utils
import common.config as config
import plugin_dir.collectd.redis as p_inst
import plugin_dir.plugin_installer_test as t_inst


class RedisConfiguratorTest(
        t_inst.PluginInstallerTest, p_inst.RedisConfigurator):
    def check_dependency(self):
        """
        requires Python >= 2.3, which is already checked.

        create /opt/collectd/plugins/python directory
        cp the redis_info.py into there
        """
        if config.DEBUG:
            plugin_src = '{}/{}'.format(
                config.PLUGIN_EXTENSION_DIR, 'redis_info.py')
        else:
            plugin_src = '{}/{}/{}'.format(
                config.APP_DIR,
                config.PLUGIN_EXTENSION_DIR,
                'redis_info.py')

        utils.print_step(
            'Begin configuring Redis python plugin for collectd')

        # create directory if it doesn't exist
        if not utils.check_path_exists(config.COLLECTD_PYTHON_PLUGIN_PATH):
            utils.print_step(
                '  Creating directory {} '
                'for collectd python plugin'.format(config.COLLECTD_PYTHON_PLUGIN_PATH))
            res = utils.call_command(
                'mkdir -p {}'.format(config.COLLECTD_PYTHON_PLUGIN_PATH))
            if res == 0:
                utils.print_success()
            else:
                utils.print_failure()
                raise Exception(
                    'Unable to create directory {}.'.format(
                        config.COLLECTD_PYTHON_PLUGIN_PATH))

        utils.print_step(
            '  Moving python plugin')
        res = utils.call_command(
            'cp {src} {dst}'.format(
                src=plugin_src, dst=config.COLLECTD_PYTHON_PLUGIN_PATH))
        if res == 0:
            utils.print_success()
        else:
            utils.print_failure()
            raise Exception('Failed to move the plugin.')

    def collect_data(self):
        """
        data = {
            instance_name: {
                host: value,
                port: value,
            (optional)
                auth: value,
                slave: bool
            }
        }
        """
        data = {
            'docker_test': {
                'host': host,
                'port': port
            }
        }
        return data


if __name__ == '__main__':
    redis = RedisConfiguratorTest(
        'DEBIAN', 'COLLECTD', 'python', 'wavefront_redis.conf')
    config.INSTALL_LOG = '/dev/stdout'
    redis.install()
