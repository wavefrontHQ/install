import re

import install_utils as utils
import plugin_installer as inst
import config


class ApacheInstaller(inst.PluginInstaller):
    def title(self):
        utils.cprint(
            ' _____ __________  _____  _________   ___ ______________\n'
            '   /  _  \\______   \/  _  \ \_   ___ \ /   |   \_   _____/\n'
            '  /  /_\  \|     ___/  /_\  \/    \  \//    ~    \    __)_ \n'
            ' /    |    \    |  /    |    \     \___\    Y    /        \ \n'
            ' \____|__  /____|  \____|__  /\______  /\___|_  /_______  /\n'
            '         \/                \/        \/       \/        \/ \n')

    def overview(self):
        utils.cprint()
        utils.cprint(
            'To enable collectd plugin with Apache, the following '
            'steps need to be taken:\n'
            '1. mod_status for apache needs to be enabled. '
            '(Default is enabled)\n'
            '2. ExtendedStatus needs to be turned on.  (Default is off)\n'
            '3. Enable the server-status handler for each virtual host.\n')

        _ = utils.cinput('Press Enter to continue')
        utils.print_step('Begin collectd Apache plugin installer')

    def check_dependency(self):
        """
        Apache checklist:
        - check curl
        - mod_status
        - extended status
        """

        utils.print_step('Checking dependency')
        if not utils.command_exists('curl'):
            utils.exit_with_failure('Curl is needed for this plugin.')

        # ubuntu check
        # Assumption:
        # -latest apache2 is installed and the installation
        # -directory is in the default place
        if self.os == config.DEBIAN:
            utils.print_step('  Checking if mod_status is enabled')
            cmd_res = utils.get_command_output('ls /etc/apache2/mods-enabled')
            if cmd_res is None:
                utils.eprint(
                    'Apache2 mods-enabled folder is not '
                    'found /etc/apache2/mods-enabled.')
                utils.print_failure()
            elif 'status.conf' not in cmd_res or 'status.load' not in cmd_res:
                utils.print_step('Enabling apache2 mod_status module.')
                ret = utils.call_command('sudo a2enmod status')
                if ret != 0:
                    utils.print_failure()
                    utils.exit_with_message('a2enmod command was not found')
                utils.print_success()
        elif self.os == config.REDHAT:
            utils.cprint()
            utils.cprint(
                'To enable server status page for the apache web,\n'
                'ensure that mod_status.so module is enabled.\n'
                'This module is often enabled by default.\n'
                '"LoadModule status_module modules/mod_status.so"\n'
                'such line should be included in one of the conf files.\n')
            _ = utils.cinput('Press Enter to continue.')

        utils.cprint()
        utils.cprint(
            'In order to fully utilize the apache plugin with collectd,\n'
            'the ExtendedStatus setting needs be turned on.\n'
            'This setting can be turned on by having "ExtendedStatus on"\n'
            'in one of the .conf file.\n')

        utils.cprint(
            'If you have already enabled this status, '
            'answer "no" to the next question.\n'
            'If you would like us to enable this status, '
            'answer "yes" and we will '
            'include a extendedstatus.conf file in your apache folder.\n')

        res = utils.ask(
            'Would you like us to enable '
            'the ExtendedStatus?')

        if res:
            # dir changes depending on the system
            # tested on Ubuntu 14.04, RHEL 7.2
            if self.os == config.DEBIAN:
                conf_dir = '/etc/apache2/conf-enabled'
                app_name = 'apache2'
            elif self.os == config.REDHAT:
                conf_dir = '/etc/httpd/conf.modules.d'
                app_name = 'httpd'

            utils.print_step('Checking if ' + conf_dir + ' exists.')
            if utils.check_path_exists(conf_dir):
                # pull config file here
                utils.print_success()
                self.include_apache_es_conf(conf_dir)
                utils.cprint(
                    'extendedstatus.conf is now included in the '
                    '{0} dir.\n'.format(conf_dir))
                utils.print_step('Restarting apache')
                ret = utils.call_command(
                    'service {app_name} restart >> '
                    '{log} 2>&1'.format(
                        app_name=app_name,
                        log=config.INSTALL_LOG))
                if ret != 0:
                    raise Exception(
                        'Failed to restart apache service.')
                utils.print_success()
            else:
                exit_with_message(
                    '{cond_dir} dir does not exist. Manual '
                    'set up is required. For help, please '
                    'consule support@wavefront.com'.format(
                        conf_dir=conf_dir))

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
