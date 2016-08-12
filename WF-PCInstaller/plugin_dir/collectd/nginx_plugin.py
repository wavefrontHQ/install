import re

import common.install_utils as utils
import plugin_dir.plugin_installer as inst
import common.config as config


class NginxInstaller(inst.PluginInstaller):
    def title(self):
        utils.cprint(
            ' ****     **         **                 \n'
            '/**/**   /**  ***** //                  \n'
            '/**//**  /** **///** ** *******  **   **\n'
            '/** //** /**/**  /**/**//**///**//** ** \n'
            '/**  //**/**//******/** /**  /** //***  \n'
            '/**   //**** /////**/** /**  /**  **/** \n'
            '/**    //***  ***** /** ***  /** ** //**\n'
            '//      ///  /////  // ///   // //   // \n')

    def overview(self):
        utils.cprint()
        utils.cprint(
            'To enable collectd plugin with Nginx, the following '
            'steps need to be taken:\n'
            '1. http_stub_status_module for nginx needs to be enabled.\n'
            '2. Enable the nginx-status page for each virtual host.\n')

        _ = utils.cinput('Press Enter to continue')
        utils.print_step('Begin collectd Nginx plugin installer')

    def check_dependency(self):
        utils.print_step('Checking dependency')
        utils.print_step('  Checking http_stub_status_module')

        cmd_res = utils.get_command_output(
            'nginx -V 2>&1 | grep -o '
            'with-http_stub_status_module')
        if cmd_res is None:
            utils.print_warn(
                'http_stub_status_module is not enabled.\n'
                'This module is required to enable the '
                'nginx-status page.')
            self.raise_error('http_stub_status_module')
        utils.print_success()

    def write_plugin(self, out):
        count = 0  # number of server being monitored

        utils.print_step('Begin writing nginx plugin for collectd')
        out.write('LoadPlugin "nginx"\n')
        out.write('<Plugin "nginx">\n')

        self.plugin_usage()

        while count == 0:  # can only monitor one for this plugin
            url = utils.get_input(
                'Please enter the url that contains your '
                'nginx-status:\n(ex: localhost/nginx-status)\n'
                '(This plugin can only monitor one server)')
            utils.cprint()
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
                res = self.check_nginx_status(res)
                if not res:
                    utils.print_warn(
                        'The url you have provided '
                        'does not seem to be the correct nginx_status '
                        'page.  Incorrect server-status will not be '
                        'recorded by collectd.')
                    res = utils.ask(
                        'Would you like to record this url anyway?', 'no')

                if res:
                    plugin_instance = (
                        '    URL "{url}"\n').format(url=url)
                    utils.cprint('Result from:\n{}'.format(plugin_instance))
                    res = utils.ask(
                        'Is this the correct url to monitor?')
                    if res:
                        count = count + 1
                        out.write(plugin_instance)
        out.write('</Plugin>\n')
        return count

    def check_nginx_status(self, payload):
        nginx_re = re.search(
            r'active connections:\s*\d+\s*'
            'server accepts handled requests', payload, re.I)
        nginx_re2 = re.search(
            r'reading: \d+ writing: \d+ waiting: \d+', payload, re.I)

        if nginx_re is None or nginx_re2 is None:
            return False

        return True

    def plugin_usage(self):
        utils.cprint(
          'To monitor a nginx server, '
          'you must enable the nginx-status page.\n'
          'To enable a nginx-status page, the following code in quote\n'
          '"location /nginx-status{\n'
          '  stub_status on;\n'
          '  access_log off;\n'
          '  allow 127.0.0.1;\n'
          '  deny all;\n'
          '}"\n'
          'must be included within a server block '
          'for the .conf file of your server.\n\n'
          'To check whether the nginx-status page is working, '
          'please visit\n'
          '\tyour-server-name/server-status\n')

if __name__ == '__main__':
    nginx = NginxInstaller('DEBIAN', 'nginx', 'wavefront_nginx.conf')
    config.INSTALL_LOG = '/dev/null'
    nginx.install()
