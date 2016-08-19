"""
Tested with Nginx/1.4.6 (Ubuntu)
"""

import common.install_utils as utils
import common.config as config
import plugin_dir.plugin_installer as inst
import plugin_dir.utils.nginx_utils as n_utils
import plugin_dir.utils.plugin_utils as p_utils
import plugin_dir.telegraf.telegraf_utils as tf_utils

class NginxConfigurator(inst.PluginInstaller):
    def title(self):
        n_utils.title()

    def overview(self):
        n_utils.overview()
        utils.print_step('Begin telegraf nginx configurator')

    def check_dependency(self):
        n_utils.check_dependency()

    def collect_data(self):
        """
        data = {
            urls = [(list of server urls)]
        }
        """
        data = {}

        n_utils.plugin_usage()
        # get a server list by passing checking function from utils
        server_list = p_utils.get_server_status_list(n_utils.check_server_url)
        data['urls'] = server_list

        return data

    def output_config(self, data, out):
        utils.cprint()
        utils.print_step('Begin writing telegraf configuration file')

        server_list = data['urls']
        count = len(server_list)
        if not count:
            return False

        conf = tf_utils.get_sample_config('nginx')
        if conf is None:
            raise Exception(
                'Cannot obtain sample config with telegraf command')

        server_list_str = p_utils.json_dumps(server_list)
          
        res = tf_utils.edit_conf(
            conf, 'urls', server_list_str)

        out.write(res)
        return True

 
if __name__ == '__main__':
    nginx = NginxConfigurator(
        'DEBIAN', 'COLLECTD', 'nginx', 'wavefront_nginx.conf')
    config.INSTALL_LOG = '/dev/stdout'
    nginx.install()
