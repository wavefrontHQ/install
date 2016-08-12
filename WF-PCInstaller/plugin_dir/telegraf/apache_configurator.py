import re

import common.install_utils as utils
import common.config as config
import plugin_dir.plugin_installer as inst
import plugin_dir.utils.apache_utils as a_utils
import plugin_dir.telegraf.telegraf_utils as tf_utils

class ApacheConfigurator(inst.PluginInstaller):
    def title(self):
        a_utils.title()

    def overview(self):
        a_utils.overview()
        utils.print_step('Begin telegraf apache configurator')

    def check_dependency(self):
        a_utils.check_dependency(self.os)

    def write_plugin(self, out):
        utils.cprint()
        utils.print_step('Begin writing telegraf configuration file')
        a_utils.apache_plugin_usage()

        server_list = self.get_server_list()
        count = len(server_list)
        if not count:
            return False


        conf = tf_utils.get_sample_config('apache')
        if conf is None:
            utils.cprint('Why is this None?')
            _ = utils.cinput('Press Enter to continue')
            raise Exception(
                'Cannot obtain sample config with telegraf command')
          
        res = self.edit_conf(conf, server_list)

        out.write(res)
        return count

    def edit_conf(self, conf, server_list):
        """
        read the sample config and modify the appropriate field

        use regex substitute urls = []
        with the proper list
        """
        # add ?auto to url in server_list and append them
        # to a string
        urls_list_str = '['
        first = True
        for url in server_list:
            if first:
                urls_list_str += '"{url}?auto"'.format(url=url)
                first = False
            else:
                urls_list_str += ', "{url}?auto"'.format(url=url)
        urls_list_str += ']'
            
        res = re.sub(
            r'urls = \[".*"\]', 
            'urls = {server_list}'.format(server_list=urls_list_str),
            conf)
        if config.DEBUG:
            utils.cprint('After change:')
            utils.cprint(res)

        return res


    def get_server_list(self):
        """
        get a list of server-status urls

        Output:
            server_list []string: list of urls
        """
        server_list = []

        while utils.ask('Would you like to add a server to monitor?'):
            url = None
            while not a_utils.check_server(url, server_list):
                url = utils.get_input(
                    'Please enter the url that contains your '
                    'server-status\n'
                    '(ex: http://www.apache.org/server-status):')

            utils.cprint()
            utils.cprint(
                'url: {}'.format(url))
            res = utils.ask(
                'Is this the correct url?')
            if res:
                utils.print_step('Saving instance')
                server_list.append(url)
                utils.print_success()
            else:
                utils.cprint('Instance is not saved.')

        return server_list
 
if __name__ == '__main__':
    apache = ApacheConfigurator(
        'DEBIAN', 'COLLECTD', 'apache', 'wavefront_apache.conf')
    config.INSTALL_LOG = '/dev/null'
    apache.install()
