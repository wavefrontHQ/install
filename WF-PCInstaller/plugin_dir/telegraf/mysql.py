"""
Tested with mysql  Ver 14.14 Distrib 5.5.49 (Ubuntu 14.04)
"""
import common.install_utils as utils
import common.config as config
import plugin_dir.plugin_installer as inst
import plugin_dir.utils.plugin_utils as p_utils
import plugin_dir.telegraf.telegraf_utils as tf_utils


class MySQLConfigurator(inst.PluginInstaller):
    def title(self):
        utils.cprint(
          ' ****     ****           ********   *******    **      \n'
          '/**/**   **/**  **   ** **//////   **/////**  /**      \n'
          '/**//** ** /** //** ** /**        **     //** /**      \n'
          '/** //***  /**  //***  /*********/**      /** /**      \n'
          '/**  //*   /**   /**   ////////**/**    **/** /**      \n'
          '/**   /    /**   **           /**//**  // **  /**      \n'
          '/**        /**  **      ********  //******* **/********\n'
          '//         //  //      ////////    /////// // ////////\n')

    def overview(self):
        utils.cprint()
        utils.cprint(
            'The telegraf MySQL plugin collects data from\n'
            'mysql server by executing query and using\n'
            'commands like SHOW STATUS.\n'
            'When asked for username and password,\n'
            'please create/provide an account for the mysql server\n'
            'this plugin will be monitoring.')

        _ = utils.cinput('Press Enter to continue')
        utils.print_step('Begin telegraf MySQL plugin configurator')

    def check_dependency(self):
        pass

    def collect_data(self):
        """
        Prompt the user for information, and guide them through the plugin

        host: (default: localhost)
        User: (any existing user will work if not monitoring replication db)
        Password:(password for the user)
        TCP: (port number, used for remote host )

        data = {
            "servers": [(list of dsn)]
        }
        """
        data = {'servers': []}
        db_list = []

        while utils.ask('\nWould you like to add a mysql server to monitor?'):
            host = utils.prompt_and_check_input(
                prompt=(
                    '\nWhat is the hostname or IP of your DB server? '
                    '(ex: 127.0.0.1)'),
                check_func=utils.hostname_resolves,
                usage='{} does not resolve.'.format,
                usage_fmt=True)

            port = utils.prompt_and_check_input(
                prompt=(
                    '\nWhat is the TCP-port used to connect to the host? '),
                check_func=utils.check_valid_port,
                usage=(
                    'A valid port is a number '
                    'between (0, 65535) inclusive.'),
                default="3306")

            if (host, port) in db_list:
                utils.cprint(
                    'You have already recorded\n'
                    '{host}:{port}'.format(
                        host=host, port=port))
                continue

            utils.cprint(
                'Please provide/create an valid account '
                'that the plugin can use to login to the server. '
                'Account with minimal privilege is sufficient.')
            username = utils.get_input(
                '\nWhat is the username?')
            password = utils.get_input(
                'What is the password?')

            instance = (
                '    User "{username}"\n'
                '    Password "{password}"\n'
                '    Host "{host}"\n'
                '    Port "{port}"\n').format(
                        username=username,
                        password=password,
                        host=host, port=port)

            utils.cprint()
            utils.cprint(
                'Result:\n{instance}'.format(instance=instance))
            res = utils.ask('Is the above information correct?')

            if res:
                utils.print_step('Saving instance')
                db_list.append((host, port))
                server = (
                    '{username}:{password}@tcp({host}:{port})').format(
                      username=username,
                      password=password,
                      host=host, port=port)
                data['servers'].append(server)
                utils.print_success()
            else:
                utils.cprint('This instance will not be saved.')

        return data

    def output_config(self, data, out):
        utils.print_step('Begin writing mysql telegraf configuration file')

        server_list = data['servers']
        count = len(server_list)
        if not count:
            return False

        conf = tf_utils.get_sample_config('mysql')
        if conf is None:
            raise Exception(
                'Cannot obtain sample config with telegraf command')

        server_list_str = p_utils.json_dumps(server_list)
        res = tf_utils.edit_conf(conf, 'servers', server_list_str)

        out.write(res)
        return count

if __name__ == '__main__':
    sql = MySQLConfigurator(
        'DEBIAN', 'COLLECTD', 'mysql', 'wavefront_mysql.conf')
    config.INSTALL_LOG = '/dev/stdout'
    sql.install()
