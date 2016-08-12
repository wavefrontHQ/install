import common.install_utils as utils
import common.config as config
import plugin_dir.plugin_installer as inst
import plugin_dir.utils.apache_utils as a_util


class ApacheInstaller(inst.PluginInstaller):
    def title(self):
        a_util.title()

    def overview(self):
        a_util.overview()
        utils.print_step('Begin collectd Apache plugin installer')

    def check_dependency(self):
        a_util.check_dependency(self.os)

    def write_plugin(self, out):
        count = 0
        server_list = []
        iname_list = []

        utils.print_step('Begin writing apache plugin for collectd')
        out.write(
            'LoadPlugin "apache"\n'
            '<Plugin "apache">\n')
        a_util.apache_plugin_usage()

        while utils.ask('Would you like to add a server to monitor?'):
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

            url = None
            while not a_util.check_server(url, server_list):
                url = utils.get_input(
                    'Please enter the url that contains your '
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
                count = count + 1
                server_list.append(url)
                iname_list.append(iname)
                out.write(plugin_instance)
                utils.print_success()
            else:
                utils.cprint('Instance is not saved.')
        out.write('</Plugin>\n')
        return count

if __name__ == '__main__':
    apache = ApacheInstaller('DEBIAN', 'apache', 'wavefront_apache.conf')
    config.INSTALL_LOG = '/dev/null'
    apache.install()
