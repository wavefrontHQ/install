"""
cassandra 3.7.0 (Ubuntu 14.04)
"""
import re

import common.install_utils as utils
import plugin_dir.plugin_installer as inst
import common.config as config


class CassandraConfigurator(inst.PluginInstaller):
    def title(self):
        utils.cprint(
            '   ____                              _           \n'
            '  / ___|__ _ ___ ___  __ _ _ __   __| |_ __ __ _ \n'
            ' | |   / _` / __/ __|/ _` | \'_ \ / _` | \'__/ _` |\n'
            ' | |__| (_| \__ \__ \ (_| | | | | (_| | | | (_| |\n'
            '  \____\__,_|___/___/\__,_|_| |_|\__,_|_|  \__,_|\n')

    def overview(self):
        utils.cprint()
        utils.cprint(
            'Overview:\n'
            'The Cassandra collectd plugin uses GenericJMX plugin\n'
            'within the java plugin to collect various\n'
            'management information from the MBeanServer.\n'
            'We have set up some common collected metrics for Cassandra.\n'
            'The information needed from the user is the access to the \n'
            'MBeanServer.\n')

        _ = utils.cinput('Press Enter to continue')
        utils.print_step('Begin collectd Cassandra plugin installer')

    def check_dependency(self):
        utils.print_step('Checking dependency')

        ldd_out = utils.get_command_output(
            'ldd {}/java.so'.format(self.plugin_dir))
        for line in ldd_out.split('\n'):
            libjvm_re = re.search(r'libjvm.so(.*?)not found', line)
            if libjvm_re is not None:
                utils.call_command(
                    'echo Missing libjvm dependency for collectd java plugin '
                    '>>{log}'.format(log=config.INSTALL_LOG))
                self.raise_error(
                    'Missing libjvm dependency for collectd java plugin.')
        utils.print_success()

    def collect_data(self):
        data = {}
        # ServiceURL "service:jmx:rmi:///jndi/rmi://localhost:7199/jmxrmi"

        utils.print_step('Begin writing Cassandra plugin for collectd')
        url = None

        url = utils.prompt_and_check_input(
            prompt=(
                '\nPlease enter a valid JMXServiceURL that can reach\n'
                'your MBeanServer'),
            default=(
                'service:jmx:rmi:'
                '///jndi/rmi://localhost:7199/jmxrmi'),
            check_func=self.check_JMXServiceURL,
            usage=self.url_usage).replace(" ", "")

        plugin_instance = (
            '      ServiceURL "{url}"\n').format(url=url)

        protected = utils.ask(
              'Is a valid account required to authenticate to '
              'the server?\n'
              '(If not, "monitorRole" will be used.)', None)
        if protected:
            user = utils.get_input(
                'What is the username?')
            password = utils.get_input(
                'What is the password?')
            plugin_instance += (
                '      User "{user}"\n'
                '      Password "{password}"\n').format(
                    user=user, password=password)

        utils.cprint()
        utils.cprint('Result:\n{}'.format(plugin_instance))
        res = utils.ask(
            'Is the above information correct?')
        if res:
            # pull and edit the conf file
            data = {
                'url': url
            }
            if protected:
                data['user'] = user
                data['password'] = password
        else:
            url = None

        return data

    def output_config(self, data, out):
        plugin_instance = (
            '      ServiceURL "{url}"\n').format(
              url=data['url'])
        if 'user' in data:
            plugin_instance += (
                '      User "{user}"\n'
                '      Password "{password}"\n').format(
                    user=data['user'],
                    password=data['password'])
        self.edit_cass_conf(out, plugin_instance)

        return True

    def edit_cass_conf(self, out, plugin_instance):
        """
        -read cass file
        -write to the temp file
        -replace ServiceURL line
        -close the read file
        """
        if config.DEBUG:
            filepath = '{conf_dir}/{conf_name}'.format(
                conf_dir=config.PLUGIN_CONF_DIR,
                conf_name=self.conf_name)
        else:
            filepath = '{app_dir}/{conf_dir}/{conf_name}'.format(
                app_dir=config.APP_DIR,
                conf_dir=config.PLUGIN_CONF_DIR,
                conf_name=self.conf_name)

        try:
            with open(filepath) as cfile:
                for line in cfile:
                    url_re = re.search(
                        r'ServiceURL "CHANGE_THIS"', line)
                    if url_re is None:
                        out.write(line)
                    else:
                        out.write(plugin_instance)
        except (IOError, OSError) as e:
            utils.eprint('Cannot open {}'.format(filepath))
            raise Exception(
                  'Error: {}\n'
                  'Cannot open {}.'.format(e, filepath))

    def check_JMXServiceURL(self, url):
        if url is None:
            return False

        # parse character following RFC 2609
        for char in url:
            c = ord(char)
            if c < 32 or c >= 127:
                utils.print_color_msg(
                    'Service URL cannot contain non-ASCII character'
                    'such as {}'.format(hex(c)), utils.YELLOW)
                return False

        url_len = len(url)

        # parse prefix
        requiredPrefix_re = re.match(r'service:jmx:(.*)', url)

        if requiredPrefix_re is None:
            utils.print_color_msg(
                'JMXServiceURL must start with service:jmx:', utils.YELLOW)
            return False

        # working example:
        # "service:jmx:rmi:///jndi/rmi://localhost:7199/jmxrmi"
        rest = requiredPrefix_re.group(1)

        # parse protocol
        rest_re = re.search(
            r'(.*?)://(.*)', rest)
        if rest_re is None:
            utils.print_color_msg(
                'Missing :// after protocol', utils.YELLOW)
            return False
        protocol = rest_re.group(1)
        if not protocol[0].isalpha():
            utils.cprint('Invalid protocol: {}'.format(protocol))
            return False

        return True

    def url_usage(self):
        utils.cprint()
        utils.cprint(
            'JMXService URL syntax:\n'
            '\tservice:jmx:rmi:sap\n'
            'where one of the accepted syntax includes:\n'
            '\tservice:jmx:rmi:///jndi/rmi://[TARGET_MACHINE]:'
            '[RMI_REGISTRY_PORT]/jmxrmi\n')

if __name__ == '__main__':
    cassandra = CassandraConfigurator(
        'DEBIAN', 'COLLECTD', 'java',
        'wavefront_cassandra.conf')
    config.INSTALL_LOG = '/dev/stdout'
    cassandra.check_dependency()
    # cassandra.install()
