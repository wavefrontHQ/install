import re

import install_utils as utils
import plugin_installer as inst

class ApacheInstaller(inst.PluginInstaller):
    def __init__(self, os, conf_name):
        super(ApacheInstaller, self).__init__(os)
        self.conf_name = conf_name

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
            '1. mod_status for apache needs to be enabled. (Default is enabled)\n'
            '2. ExtendedStatus needs to be turned on.  (Default is off)\n'
            '3. Enable the server-status handler for each virtual host.\n')

        _ = utils.cinput('Press Enter to continue')
        utils.print_step('Begin collectd Apache plugin installer')
        

    def check_dependency(self):
       # check point
        #  - check dependency
        #  - change system file
        #  - check mod status
        #  - TODO: pull template
        #  - prompt for user information
        if not utils.command_exists('curl'):
            utils.exit_with_failure('Curl is needed for this plugin.')

        # ubuntu check
        # Assumption:
        # -latest apache2 is installed and the installation
        # -directory is in the default place
        utils.print_step('  Checking if mod_status is enabled')
        cmd_res = utils.get_command_output('ls /etc/apache2/mods-enabled')
        if 'status.conf' not in cmd_res or 'status.load' not in cmd_res:
            utils.print_step('Enabling apache2 mod_status module.')
            ret = utils.call_command('sudo a2enmod status')
            if ret != 0:
                utils.exit_with_message('a2enmod command was not found')
        utils.print_success()
        utils.cprint()
        utils.cprint(
            'In order to enable the apache plugin with collectd, the '
            'ExtendedStatus setting must be turned on.\n'
            'This setting can be turned on by having "ExtendedStatus on" '
            'in one of the .conf file.\n')

        utils.cprint(
            'If you have already enabled this status, '
            'answer "no" to the next question.\n'
            'If you would like us to enable this status, answer "yes" and we will '
            'include a extendedstatus.conf file in your apache folder.\n')

        res = utils.ask(
            'Would you like us to enable '
            'the ExtendedStatus?')

        # missing the flow where user wants to turn on the setting themselves.
        if res:
            # include the config file in /apache2/conf-enabled
            conf_dir = '/etc/apache2/conf-enabled'
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
                    'service apache2 restart >> ' +
                    config.INSTALL_LOG + ' 2>&1')
                if ret != 0:
                    utils.exit_with_message('Failed to restart apache service.')
                utils.print_success()
            else:
                exit_with_message(conf_dir + ' dir does not exist, ' +
                                  'please consult support@wavefront.com' +
                                  'for help.')

    def write_plugin(self, out):
        utils.print_step('Begin writing apache plugin for collectd')
        out.write('LoadPlugin "apache"\n')
        out.write('<Plugin "apache">\n')

        count = 0
        server_list = []

        self.apache_plugin_usage()
        utils.cprint(
            'To check whether the server-status page is working, please visit\n'
            '\tyour-server-name/server-status\n'
            'It should look similar to\n'
            '\tapache.org/server-status\n')

        while utils.ask('Would you like to add a server to monitor?'):
            url = utils.get_input(
                'Please enter the url that contains your ' +
                'server-status (ex: www.apache.org/server_status):')
            utils.cprint()
            utils.print_step('Checking http response for %s' % url)
            res = utils.get_command_output('curl -s -i '+url)

            if res is None:
                ret = INVALID_URL
            else:
                ret = self.check_http_response(res)

            if ret == NOT_AUTH:
                # skip for this case for now, ask for user/pass
                utils.eprint(
                    'Authorization server status is required, please '
                    'try again.\n')
            elif ret == NOT_FOUND or ret == INVALID_URL:
                utils.print_failure()
                utils.eprint(
                    'Invalid url was provided, please try '
                    'again.\n')
            elif ret == HTTP_OK:
                utils.print_success()
                if url in server_list:
                    utils.print_warn(
                        'You have already added this server instance.')
                else:
                    res = self.check_apache_server_status(res)
                    if res is None:
                        utils.print_warn(
                            'The url you have provided '
                            'does not seem to be the correct server_status '
                            'page.  Incorrect server-status will not be recorded '
                            'by collectd.')
                        utils.ask(
                            'Would you like to record this url anyway?', 'no')
                    else:
                        utils.cprint(res)
                        res = utils.ask('Is this the correct status to monitor?')
                        utils.cprint()
                        if res:
                            count = count + 1
                            server_list.append(url)
                            instance = 'apache%d' % count
                            url_auto = url+'?auto'
                            plugin_instance = (
                                '  <Instance "{instance}">\n'
                                '    URL "{url}"\n'
                                '  </Instance>\n').format(instance=instance,
                                                          url=url_auto)
                            out.write(plugin_instance)

        out.write('</Plugin>\n')
        return count

    def check_http_response(http_res):
        http_status_re = re.match('HTTP/1.1 (\d* [\w ]*)\s', http_res)
        if http_status_re is None:
            utils.print_warn('Invalid http response header!')
            sys.exit(1)

        http_code = http_status_re.group(1)

        if('401 Unauthorized' in http_code):
            return NOT_AUTH
        elif('404 Not Found' in http_code):
            return NOT_FOUND
        elif('200 OK' in http_code):
            return HTTP_OK
        else:
            return INVALID_URL


    def check_apache_server_status(payload):
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

    def include_apache_es_conf(conf_dir):
        """
        Assume extendedstatus.conf is unique to wavefront and writing over it.
        """
        filename = 'extendedstatus.conf'
        out = utils.write_file('{conf_dir}/{filename}'.format(
                  conf_dir=conf_dir, filename=filename))
        if out is None:
            utils.exit_with_message('Unexpected error!')

        out.write(
            '# ExtendedStatus controls whether Apache will generate '
            '"full" status\n'
            '# information (ExtendedStatus On) '
            'or just basic information (ExtendedStatus\n'
            '# Off) when the "server-status" handler is called. '
            'The default is Off.\n'
            'ExtendedStatus on')
        out.close()


    def apache_plugin_usage(self):
        utils.cprint(
          'To monitor a apache server, '
          'you must enable the server-status page.\n'
          'To enable a server-status page, the following code in quote\n'
          '"<Location /server-status>\n'
          '  SetHandler server-status\n'
          '</Location>"\n'
          'must be included within a <VirtualHost> block '
          'for the .conf file of your server.\n')



if __name__ == '__main__':
    apache = ApacheInstaller('Debian', 'wavefront_apache.conf')
    apache.install()
