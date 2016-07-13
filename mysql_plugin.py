import sys
import re
import socket

import install_utils as utils
import plugin_installer as inst
import config


class MySQLInstaller(inst.PluginInstaller):
    def __init__(self, os, conf_name):
        super(MySQLInstaller, self).__init__(os)
        self.conf_name = conf_name

    def get_conf_name(self):
       return self.conf_name

    def title(self):
        art = (
          ' ****     ****           ********   *******    **      \n'
          '/**/**   **/**  **   ** **//////   **/////**  /**      \n'
          '/**//** ** /** //** ** /**        **     //** /**      \n'
          '/** //***  /**  //***  /*********/**      /** /**      \n'
          '/**  //*   /**   /**   ////////**/**    **/** /**      \n'
          '/**   /    /**   **           /**//**  // **  /**      \n'
          '/**        /**  **      ********  //******* **/********\n'
          '//         //  //      ////////    /////// // ////////\n')
        utils.cprint(art)

    def overview(self):
        utils.cprint()
        utils.cprint(
            'The collectd MySQL plugin collects data from '
            'the SHOW STATUS command in mysqlclient. '
            'The SHOW STATUS command can be used by user of '
            'any priviledge.\nWhen asked for a user account, '
            'please create one under the mysql server '
            'the collectd will be monitoring.')

        _ = utils.cinput('Press Enter to continue')

        utils.print_step('Begin collectd MySQL plugin installer')

    def check_dependency(self):
        pass

    def check_valid_port(self, s):
        if s is None:
            return False

        try:
            num = int(s)
        except ValueError:
            utils.eprint(
                '{} is not a valid port. '
                'A valid port is a number '
                'between (0, 65535) inclusive.'.format(s))
            return False

        if num < 0 or num > 65535:
            utils.eprint(
                '{} is not a valid port. '
                'A valid port is a number '
                'between (0, 65535) inclusive.'.format(s))
            return False

        return True

    def is_valid_ipv4_address(self, address):
        """
        from stack overflow

        source: http://stackoverflow.com/questions/319279/how-to-validate-ip-address-in-python/4017219#4017219
        """
        try:
            socket.inet_pton(socket.AF_INET, address)
        except AttributeError:  # no inet_pton here, sorry
            try:
                socket.inet_aton(address)
            except socket.error:
                return False
            return address.count('.') == 3
        except socket.error:  # not a valid address
            return False

        return True

    def check_socket_path(self, path):
        if path is None:
            return False
        # if it begins with ~ then do expand user

        socket_re = re.match(r'mysqld.sock$|(~/|/)(.*/)*mysqld.sock$', path)
        if socket_re is None:
            utils.eprint(
                'Invalid path was given.\n'
                ' -Path has to end with mysqld.sock.\n'
                ' -If relative path is used, please add ~/ '
                'to the beginning')
            return False

        if socket_re.group(1) == '~/':
            res = utils.check_path_exists(path, expand=True, debug=True)
        else:
            res = utils.check_path_exists(path, debug=True)

        if not res:
            utils.eprint(
                'Invalid path was given. '
                'Could not find mysqld.sock with the given path.')

        return res

    def write_plugin(self, out):
        """
        Prompt the user for information, and guide them through the plugin

        host: (default: localhost)
        User: (any existing user will work if not monitoring replication db)
        Password:(password for the user)
        Socket: ( path to sockt, used for localhost )
        TCP: (port number, used for remote host )
        * Database: (the specific db to monitor)
            * This option doesn't seem to affect anything with
            * the collectd plugin
        """

        utils.print_step('Begin writing MySQL plugin for collectd')
        out.write('LoadPlugin "mysql"\n')
        out.write('<Plugin "mysql">\n')
        utils.cprint('')

        count = 0
        db_list = []
        default_socket_path = '/var/run/mysqld/mysqld.sock'

        while utils.ask('Would you like to add a DB server to monitor?'):
            db = utils.get_input(
                'How would you like to name this DB server?')

            if db in db_list:
                utils.cprint('You have already recorded this db')
                continue

            remote = utils.ask(
                'Is this a remote host?')

            if remote:
                host = ''
                while(not self.is_valid_ipv4_address(host)):
                    host = utils.get_input(
                        'What is the hostname of your DB server? '
                        '(ex: 127.0.0.1)')

                port = None
                while(not self.check_valid_port(port)):
                    port = utils.get_input(
                        'What is the TCP-port used to connect to the host? '
                        '(ex: 3306)')
            else:
                socket = None
                while(not self.check_socket_path(socket)):
                    socket = utils.get_input(
                        'What is the path to your mysqld.sock?',
                        default_socket_path)

            utils.cprint(
                'Please provide/create an valid account '
                'that the plugin can use to login to the server. '
                'Account with minimal privilege is sufficient.')
            username = utils.get_input(
                'What is the username?')
            password = utils.get_input(
                'What is the password?')

            instance = (
                '    User "{username}"\n'
                '    Password "{password}"\n').format(
                        username=username,
                        password=password)

            if remote:
                instance += (
                    '    Host "{}"\n'
                    '    Port "{}"\n'.format(host, port))
            else:
                instance += (
                    '    Host "localhost"\n'
                    '    Socket "{}"\n'.format(socket))

            utils.cprint()
            utils.cprint(
                'Database {}\n'
                '{}'.format(db, instance))
            res = utils.ask('Is the above information correct?')

            if res:
                utils.print_step('Saving instance')
                db_list.append(db)
                count += 1
                out.write(
                    '  <Database {db}>\n'
                    '{instance}'
                    '  </Database>\n'.format(db=db, instance=instance))
                utils.print_success()
            else:
                utils.cprint('This instance will not be saved.')

        out.write('</Plugin>\n')
        return count


if __name__ == '__main__':
    sql = MySQLInstaller('Debian', 'wavefront_mysql.conf')
    sql.install()
