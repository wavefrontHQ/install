"""
Tested with Apache/2.4.7 (Ubuntu 14.04)
"""

import common.install_utils as utils
import common.config as config
import plugin_dir.plugin_installer as inst
import plugin_dir.utils.apache_utils as a_util


class ApacheConfigurator(inst.PluginInstaller):
    def title(self):
        a_util.title()

    def overview(self):
        a_util.overview()
        utils.print_step('Begin collectd Apache plugin installer')

    def check_dependency(self):
        a_util.check_dependency(self.os)

    def collect_data(self):
        """
        data = {
            "instance_name": "url",
        }
        """
        data = {}
        server_list = []
        iname_list = []

        a_util.plugin_usage()
        while utils.ask('Would you like to add a server to monitor?'):
            # Ask for a instance name that isn't already recorded
            iname = utils.prompt_and_check_input(
                prompt=(
                    '\nHow would you like to name this monitoring instance?\n'
                    '(How it should appear on your wavefront metric page, \n'
                    'space between words will be removed)'),
                check_func=(
                    lambda x: x.replace(" ", "") not in iname_list),
                usage=(
                    '{} has already been used.'.format),
                usage_fmt=True).replace(" ", "")

            # ask for a valid server status url
            url = None
            while not a_util.check_server_url(url, server_list):
                url = utils.get_input(
                    '\nPlease enter the url that contains your '
                    'server-status\n'
                    '(ex: http://www.apache.org/server-status):')

            url_auto = url+'?auto'
            plugin_instance = (
                '  <Instance "{instance}">\n'
                '    URL "{url}"\n'
                '  </Instance>\n').format(instance=iname,
                                          url=url_auto)
            utils.cprint()
            utils.cprint(
                'Your url is appended with ?auto to convert '
                'the content into machine readable code.\n'
                '{}'.format(plugin_instance))
            res = utils.ask(
                'Is this the correct status to monitor?')
            if res:
                utils.print_step('Saving instance')
                # store input
                server_list.append(url)
                iname_list.append(iname)
                data[iname] = url_auto
                utils.print_success()
            else:
                utils.cprint('Instance is not saved.')

        return data

    def output_config(self, data, out):
        utils.print_step('Begin writing apache plugin for collectd')
        if not data:
            return False

        out.write(
            'LoadPlugin "apache"\n'
            '<Plugin "apache">\n')

        for instance in data:
            out.write(
                '  <Instance "{instance}">\n'
                '    URL "{url}"\n'
                '  </Instance>\n'.format(instance=instance,
                                         url=data[instance]))

        out.write('</Plugin>\n')
        return True

if __name__ == '__main__':
    apache = ApacheInstaller(
        'DEBIAN', 'COLLECTD', 'apache', 'wavefront_apache.conf')
    config.INSTALL_LOG = '/dev/stdout'
    apache.install()
