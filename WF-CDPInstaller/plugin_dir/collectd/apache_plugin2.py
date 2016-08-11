import re

import common.install_utils as utils
import common.config as config
import plugin_dir.plugin_installer as inst
import plugin_dir.common.apache_utilities as a_util


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
        sv_list = []
        overwrite = True

        utils.print_step('Begin writing apache plugin for collectd')
        out.write('LoadPlugin "apache"\n')
        out.write('<Plugin "apache">\n')
        self.apache_plugin_usage()

        while utils.ask('Would you like to add a server to monitor?'):
            sv_name = utils.get_input(
                'How would you like to name this server? '
                '(space between words will be removed)').replace(" ", "")

            if sv_name in sv_list:
                utils.cprint('You have already used {}.'.format(
                    sv_name))
                continue

            url = utils.get_input(
                'Please enter the url that contains your '
                'server-status (ex: www.apache.org/server_status):')
            utils.cprint()

            if url in server_list:
                utils.eprint(
                    'You have already added this {} server.'.format(url))
                continue

            utils.print_step('Checking http response for %s' % url)
            res = utils.get_command_output('curl -s -i '+url)

            if res is None:
                ret = utils.INVALID_URL
            else:
                ret = utils.check_http_response(res)

            if ret == utils.NOT_AUTH:
                # skip for this case for now, ask for user/pass
                utils.eprint(
                    'Authorization server status is required, please '
                    'try again.\n')
            elif ret == utils.NOT_FOUND or ret == utils.INVALID_URL:
                utils.print_failure()
                utils.eprint(
                    'Invalid url was provided, please try '
                    'again.\n')
            elif ret == utils.HTTP_OK:
                utils.print_success()
                overwrite = True
                status = self.check_apache_server_status(res)
                if status is None:
                    utils.print_warn(
                        'The url you have provided '
                        'does not seem to be the correct server_status '
                        'page.  Incorrect server-status will not be '
                        'recorded by collectd.')
                    overwrite = utils.ask(
                        'Would you like to record this url anyway?', 'no')

                if overwrite:
                    if status:
                        utils.cprint(status)
                    url_auto = url+'?auto'
                    plugin_instance = (
                        '  <Instance "{instance}">\n'
                        '    URL "{url}"\n'
                        '  </Instance>\n').format(instance=sv_name,
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
                        sv_list.append(sv_name)
                        out.write(plugin_instance)
                        utils.print_success()
                    else:
                        utils.cprint('Instance is not saved.')
        out.write('</Plugin>\n')
        return count

    def check_apache_server_status(self, payload):
        atitle_re = re.search(
            r'(<head>[\w\W\s]*<title>Apache '
            'Status</title>[\w\W\s]*</head>)([\w\W\s]*)', payload)

        if atitle_re is not None:
            res = atitle_re.group(2)
            ah1_re = re.search(
                r'<h1>(Apache Server Status for )([\w\W]*?)</h1>',
                res)
            if ah1_re is not None:
                res = ah1_re.group(1) + ah1_re.group(2)
                return res

        return None

    def include_apache_es_conf(self, conf_dir):
        """
        Assume extendedstatus.conf is unique to wavefront and writing over it.
        """
        filename = 'extendedstatus.conf'
        filepath = '{conf_dir}/{filename}'.format(
                  conf_dir=conf_dir, filename=filename)
        content = (
            '# ExtendedStatus controls whether Apache will generate '
            '"full" status\n'
            '# information (ExtendedStatus On) '
            'or just basic information (ExtendedStatus\n'
            '# Off) when the "server-status" handler is called. '
            'The default is Off.\n'
            'ExtendedStatus on')

        out = utils.write_file(filepath, content)

    def apache_plugin_usage(self):
        utils.cprint(
          'To monitor a apache server, '
          'you must enable the server-status page.\n'
          'To enable a server-status page, the following code in quote\n'
          '"<Location /server-status>\n'
          '  SetHandler server-status\n'
          '</Location>"\n'
          'must be included within a <VirtualHost> block '
          'for the .conf file of your server.\n\n'
          'To check whether the server-status page is working, '
          'please visit\n'
          '\tyour-server-name/server-status\n'
          'It should look similar to\n'
          '\tapache.org/server-status\n')

if __name__ == '__main__':
    apache = ApacheInstaller('DEBIAN', 'apache', 'wavefront_apache.conf')
    config.INSTALL_LOG = '/dev/null'
    apache.install()
