"""
Tested with Apache/2.4.7 (Ubuntu 14.04)
"""

import common.install_utils as utils
import common.config as config
import plugin_dir.plugin_installer as inst
import plugin_dir.utils.apache_utils as a_utils
import plugin_dir.utils.plugin_utils as p_utils
import plugin_dir.telegraf.telegraf_utils as tf_utils


class ApacheConfigurator(inst.PluginInstaller):
    def title(self):
        a_utils.title()

    def overview(self):
        a_utils.overview()
        utils.print_step('Begin telegraf apache configurator')

    def check_dependency(self):
        a_utils.check_dependency(self.os)

    def collect_data(self):
        """
        data = {
            urls = [(list of server urls)]
        }
        """
        data = {}
        a_utils.plugin_usage()

        # get a server list by passing checking function from utils
        server_list = p_utils.get_server_status_list(a_utils.check_server_url)
        data['urls'] = server_list

        return data

    def output_config(self, data, out):
        utils.cprint()
        utils.print_step('Begin writing telegraf configuration file')

        server_list = data['urls']
        count = len(server_list)
        if not count:
            return False

        conf = tf_utils.get_sample_config('apache')
        if conf is None:
            raise Exception(
                'Cannot obtain apache sample config with telegraf command')

        # add ?auto to url in server_list
        # replace ' with " for toml format
        url_list_str = p_utils.json_dumps(
            [url+"?auto" for url in server_list])
        res = tf_utils.edit_conf(conf, 'urls', url_list_str)

        out.write(res)
        return count

if __name__ == '__main__':
    apache = ApacheConfigurator(
        'DEBIAN', 'COLLECTD', 'apache', 'wavefront_apache.conf')
    config.INSTALL_LOG = '/dev/stdout'
    apache.install()
