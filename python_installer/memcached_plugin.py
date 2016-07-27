import re

import install_utils as utils
import plugin_installer as inst
import config


class MemcachedInstaller(inst.PluginInstaller):
    def title(self):
        utils.cprint(
  ' __  __                                     _                _ '
  '|  \/  |                                   | |              | |'
  '| \  / |  ___  _ __ ___    ___  __ _   ___ | |__    ___   __| |'
  '| |\/| | / _ \| \'_ ` _ \  / __|/ _` | / __|| \'_ \  / _ \ / _` |'
  '| |  | ||  __/| | | | | || (__| (_| || (__ | | | ||  __/| (_| |'
  '|_|  |_| \___||_| |_| |_| \___|\__,_| \___||_| |_| \___| \__,_|')

    def overview(self):
        utils.cprint()
        utils.cprint(
            'The memcached plugin connects to a memcached server\n'
            'and queries statistics about cache utilization,\n'
            'memory and bandwidth used.\n\n'
            'To enable collectd memcached plugin,\n'
            'We just need the hostname and the port to connect\n'
            'to the memcached server.')

        _ = utils.cinput('Press Enter to continue')
        utils.print_step('Begin collectd Memcached plugin installer')

    def check_dependency(self):
        pass

    def write_plugin(self, out):
        count = 0  # number of server being monitored
        iname_list = []
        first_prompt = True

        utils.print_step('Begin writing memcached plugin for collectd')
        out.write('LoadPlugin "memcached"\n')
        out.write('<Plugin "memcached">\n')

        while utils.ask('Would you like to add a server to monitor?'):
            iname = utils.get_input(
                'How would you like to name this monitoring instance?\n'
                '(How it should appear on your wavefront metric page, \n'
                'space between words will be removed)').replace(" ", "")

            if iname in iname_list:
                utils.cprint('You have already used {}.'.format(
                    iname))
                continue

            while first_prompt or not hostname_resolves(host):
                if first prompt:
                    first_prompt = False
                else:
                    utils.cprint(
                        '{host} does not resolve.'.format(host=host))
                host = utils.get_input(
                    'Please enter the hostname that connects to your '
                    'memcached server:', '127.0.0.1')
            utils.cprint()

            port = prompt_and_check_input(
                prompt=(
                    'What is the TCP-port used to connect to the host? '
                    '(ex: 5432)'),
                check_func=utils.check_valid_port,
                usage=(
                    '{} is not a valid port.\n'
                    'A valid port is a number '
                    'between (0, 65535) inclusive.'.format(string))

            while first_prompt or not utils.check_valid_port(port):
                if first prompt:
                    first_prompt = False
                else:
                    utils.eprint(
                        '{} is not a valid port.\n'
                        'A valid port is a number '
                        'between (0, 65535) inclusive.'.format(string))
                port = utils.get_input(
                    'What is the TCP-port used to connect to the host? '
                    '(ex: 5432)')


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
                        count = count + 1
                        server_list.append(url)
                        sv_list.append(sv_name)
                        out.write(plugin_instance)
                    else:
                        utils.cprint('Instance is not saved.')
        out.write('</Plugin>\n')
        return count

if __name__ == '__main__':
    mc = MemcachedInstaller(
        'DEBIAN', 'memcached', 'wavefront_memcached.conf')
    config.INSTALL_LOG = '/dev/null'
    mc.install()
