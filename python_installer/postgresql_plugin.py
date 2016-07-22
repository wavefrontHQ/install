import plugin_installer as inst
import install_utils as utils
import config


class PostgresqlInstaller(inst.PluginInstaller):
    def title(self):
        utils.cprint(
            "______         _                       _____  _____ _     \n"
            "| ___ \       | |                     /  ___||  _  | |    \n"
            "| |_/ /__  ___| |_ __ _ _ __ ___  ___ \ `--. | | | | |    \n"
            "|  __/ _ \/ __| __/ _` | '__/ _ \/ __| `--. \| | | | |    \n"
            "| | | (_) \__ \ || (_| | | |  __/\__ \/\__/ /\ \/' / |____\n"
            "\_|  \___/|___/\__\__, |_|  \___||___/\____/  \_/\_\_____/\n"
            "                   __/ |                                  \n"
            "                  |___/                                  ")

    def overview(self):
        utils.cprint()
        utils.cprint(
            'Overview:\n'
            'The postgres collectd plugin connects to and \n'
            'execute SQL statement on a PostgreSQL database.\n'
            'It then uses the returned value as metric.\n'
            'Custom query and function tracking is possible,\n'
            'but it requires the user to be familiar with the\n'
            'configuration format. Our default configuration\n'
            'makes use of the posgres statistics collector.\n'
            'To enable the monitoring, the plugin requires\n'
            'a valid user account that has access to the\n'
            'database and has the ability to read from the database.')

        utils.cprint()
        _ = utils.cinput('Press Enter to continue')
        utils.print_step('Begin collectd PostgreSQl plugin installer')

    def check_dependency(self):
        """
        statistical collector needs to be enabled.
          - track activities:
                Enables monitoring of the current command being executed
                by any server process
          - track_counts:
                Controls whether statistics are collected about tables
                and index accesses
        """
        utils.cprint()
        utils.cprint(
            'To make use of the statistical collecter,\n'
            'our configuration requires the following\n'
            'two parameters to be turned on\n'
            '  - track_activities\n'
            '  - track_counts\n'
            'They are usually enabled by default and can\n'
            'be found at postgresql.conf.')
        utils.cprint()
        _ = utils.cinput('Press Enter to continue')

    def write_plugin(self, out):
        """
        unique query name
          - query_list = []
        Result block define how each value should be handled
          - requires Type to be specified
          - instanceprefix should be unique
        """
        comment = (
            '# Documentation:\n'
            '#   https://collectd.org/wiki/index.php/'
            'Plugin:PostgreSQL\n\n')

        sample_query_block = (
            '  <Query custom_deadlocks>\n'
            '      Statement "SELECT deadlocks as num_deadlocks \\\n'
            '          FROM pg_stat_database \\\n'
            '          WHERE datname = $1;"\n\n'
            '      Param database\n\n'
            '      <Result>\n'
            '          Type "pg_xact"\n'
            '          InstancePrefix "num_deadlocks"\n'
            '          ValuesFrom "num_deadlocks"\n'
            '      </Result>\n'
            '  </Query>\n')

        default_query = (
            '    Query custom_deadlocks\n'
            '    Query backends\n'
            '    Query transactions\n'
            '    Query queries\n'
            '    Query queries_by_table\n'
            '    Query query_plans\n'
            '    Query table_states\n'
            '    Query query_plans_by_table\n'
            '    Query table_states_by_tables\n'
            '    Query disk_io\n'
            '    Query disk_io_by_table\n'
            '    Query disk_usage\n')

        count = 0  # track how many db is monitored
        name_list = []  # keep a list of db name to check for uniqueness

        utils.cprint()
        utils.print_step('Begin writing PostgresSQL plugin for collectd')
        out.write(comment)
        out.write('LoadPlugin "postgresql"\n'
                  '<Plugin "postgresql">\n'
                  '{sample_query}\n'.format(
                      sample_query=sample_query_block))

        while utils.ask('Would you like to add a database to monitor?'):
            db = utils.get_input(
                'What is the name of the database?\n'
                '(The name should match your database name)')

            iname = utils.get_input(
                'How would you like to name this monitoring instance?\n'
                '(How it should appear on your wavefront metric page, \n'
                'space between words will be removed)').replace(" ", "")

            while iname in name_list:
                utils.cprint(
                    '{iname} has already been used.'.format(
                        iname=iname))
                iname = utils.get_input(
                    'How would you like to name this monitoring instance?')

            host = ''
            while(not utils.is_valid_ipv4_address(host)):
                host = utils.get_input(
                    'What is the hostname of your DB server? '
                    '(ex: 127.0.0.1)')

            port = None
            while(not utils.check_valid_port(port)):
                port = utils.get_input(
                    'What is the TCP-port used to connect to the host? '
                    '(ex: 5432)')

            utils.cprint(
                'Please provide/create an valid account '
                'that the plugin can use to login to the server. ')
            username = utils.get_input(
                'What is the username?')
            password = utils.get_input(
                'What is the password?')

            instance = (
                '    Host "{host}"\n'
                '    Port "{port}"\n'
                '    User "{username}"\n'
                '    Password "{password}"\n'
                '    Instance "{iname}"\n').format(
                    host=host, port=port,
                    username=username,
                    password=password,
                    iname=iname)

            utils.cprint()
            utils.cprint(
                'Database {}\n'
                '{}'.format(db, instance))
            res = utils.ask('Is the above information correct?')

            if res:
                utils.print_step('Saving instance')
                name_list.append(iname)
                count += 1
                out.write(
                    '  <Database {db}>\n'
                    '{instance}'
                    '{query}'
                    '  </Database>\n\n'.format(
                        db=db, instance=instance, query=default_query))
                utils.print_success()
            else:
                utils.cprint('This instance will not be saved.')

        out.write('</Plugin>\n')
        return count

if __name__ == '__main__':
    postgres = PostgresqlInstaller('DEBIAN', 'wavefront_postgres.conf')
    config.INSTALL_LOG = '/dev/null'
    postgres.install()
