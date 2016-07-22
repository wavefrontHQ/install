import sys
import re

import install_utils as utils
import plugin_installer as inst
import config


class MySQLInstaller(inst.PluginInstaller):
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
            'The collectd MySQL plugin collects data from\n'
            'the SHOW STATUS command in mysqlclient.\n'
            'The SHOW STATUS command can be used by user of\n'
            'any priviledge.\nWhen asked for a user account,\n'
            'please create one under the mysql server\n'
            'the collectd will be monitoring.')

        _ = utils.cinput('Press Enter to continue')

        utils.print_step('Begin collectd MySQL plugin installer')

    def check_dependency(self):
        pass

    def check_socket_path(self, path):
        if path is None:
            return False
        # if it begins with ~ then do expand user

        if self.os == config.DEBIAN:
            socket_re = re.match(
                r'mysqld.sock$|(~/|/)(.*/)*mysqld.sock$', path)
        if self.os == config.REDHAT:
            socket_re = re.match(
                r'mysql.sock$|(~/|/)(.*/)*mysql.sock$', path)

        if socket_re is None:
            utils.eprint(
                'Invalid path was given.\n'
                ' -filename has to end with .sock.\n'
                ' -Debian uses mysqld.sock, Redhat uses mysql.sock\n'
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
                'Could not find {}.'.format(path))

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
        if self.os == config.DEBIAN:
            default_socket_path = '/var/run/mysqld/mysqld.sock'
        if self.os == config.REDHAT:
            default_socket_path = '/var/lib/mysql/mysql.sock'

        while utils.ask('Would you like to add a DB server to monitor?'):
            db = utils.get_input(
                'How would you like to name this DB '
                'server? (Space between words will be '
                'removed)').replace(" ", "")

            if db in db_list:
                utils.cprint('You have already recorded this db')
                continue

            remote = utils.ask(
                'Is this a remote host?')

            if remote:
                host = ''
                while(not utils.is_valid_ipv4_address(host)):
                    host = utils.get_input(
                        'What is the hostname of your DB server? '
                        '(ex: 127.0.0.1)')

                port = None
                while(not utils.check_valid_port(port)):
                    port = utils.get_input(
                        'What is the TCP-port used to connect to the host? '
                        '(ex: 3306)')
            else:
                socket = None
                while(not self.check_socket_path(socket)):
                    socket = utils.get_input(
                        'What is the path to your mysql sock file?',
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
    sql = MySQLInstaller('DEBIAN', 'mysql', 'wavefront_mysql.conf')
    sql.install()
