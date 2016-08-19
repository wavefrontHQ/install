"""
Tested with Nginx/1.4.6 (Ubuntu 14.04)
"""

import re

import common.install_utils as utils
import common.config as config
import plugin_dir.plugin_installer as inst
import plugin_dir.utils.nginx_utils as n_utils


class NginxInstaller(inst.PluginInstaller):
    def title(self):
        n_utils.title()

    def overview(self):
        n_utils.overview()
        utils.print_step('Begin collectd Nginx plugin installer')

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

        record = True
        url = None
        while record:
            while not n_utils.check_server_url(url):
                url = utils.get_input(
                    '\nPlease enter the url that contains your '
                    'server-status:\n(ex: http://localhost/server-status)\n'
                    '(This plugin can only monitor one server)')

            plugin_instance = (
                        '    URL "{url}"\n'.format(url=url))
            utils.cprint('Result from:\n{}'.format(plugin_instance))
            res = utils.ask(
                'Is this the correct url to monitor?')
            if res:
                data['url'] = url
                record = False

        return data

    def output_config(self, data, out):
        utils.print_step('Begin writing nginx plugin for collectd')
        out.write(
            'LoadPlugin "nginx"\n'
            '<Plugin "nginx">\n'
            '  URL "{url}"\n'
            '</Plugin>\n'.format(url=data['url']))

        return True

if __name__ == '__main__':
    nginx = NginxInstaller(
        'DEBIAN', 'COLLECTD', 'nginx', 'wavefront_nginx.conf')
    config.INSTALL_LOG = '/dev/stdout'
    nginx.install()
