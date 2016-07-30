import install_utils as utils
import plugin_installer as inst
import config


class RedisInstaller(inst.PluginInstaller):
    def title(self):
        utils.cprint(
            ",-.----.                                              \n" 
            "\    /  \                  ,---,  ,--,                \n" 
            ";   :    \               ,---.'|,--.'|                \n" 
            "|   | .\ :               |   | :|  |,      .--.--.    \n" 
            ".   : |: |    ,---.      |   | |`--'_     /  /    '   \n" 
            "|   |  \ :   /     \   ,--.__| |,' ,'|   |  :  /`./   \n" 
            "|   : .  /  /    /  | /   ,'   |'  | |   |  :  ;_     \n" 
            ";   | |  \ .    ' / |.   '  /  ||  | :    \  \    `.  \n" 
            "|   | ;\  \\'   ;   /|'   ; |:  |'  : |__   `----.   \ \n" 
            ":   ' | \.''   |  / ||   | '/  '|  | '.'| /  /`--'  / \n" 
            ":   : :-'  |   :    ||   :    :|;  :    ;'--'.     /  \n" 
            "|   |.'     \   \  /  \   \  /  |  ,   /   `--'---'   \n" 
            "`---'        `----'    `----'    ---`-'               \n")

    def overview(self):
        utils.cprint()
        utils.cprint(
            'This redis plugin makes use of collectd python\n'
            'extension to connects to one or more\n'
            'Redis servers and gathers information\n'
            'about each server\'s state.\n'
            'To enable this plugin, hostname and port\n'
            'will be needed to connect to redis-server.\n')

        _ = utils.cinput('Press Enter to continue')
        utils.print_step('Begin collectd Memcached plugin installer')

    def check_dependency(self):
        """
        requires Python >= 2.3, which is already checked.
        """
        pass

    def write_plugin(self, out):
        """
        Flow:
        create /opt/collectd/plugins/python directory
        mv the redis_info.py into there
        ask for instance name
        then ask for hostname, port
        ask for auth
        """
        count = 0  # number of server being monitored
        iname_list = []
        server_list = []
        first_prompt = True
        python_plugin_path = '/opt/collectd/plugins/python'
        if config.DEBUG:
            plugin_src = '{}/{}'.format(
                config.PLUGIN_EXTENSION_DIR, 'redis_info.py')
        else:
            plugin_src = '{}/{}/{}'.format(
                config.APP_DIR,
                config.PLUGIN_EXTENSION_DIR,
                'redis_info.py')

        metrics = (
            '    Verbose false\n'
            '    # Catch Redis metrics (prefix with Redis_)\n'
            '    Redis_uptime_in_seconds "gauge"\n'
            '    Redis_used_cpu_sys "counter"\n'
            '    Redis_used_cpu_user "counter"\n'
            '    Redis_used_cpu_sys_children "counter"\n'
            '    Redis_used_cpu_user_children "counter"\n'
            '    Redis_uptime_in_days "gauge"\n'
            '    Redis_lru_clock "counter"\n'
            '    Redis_connected_clients "gauge"\n'
            '    Redis_connected_slaves "gauge"\n'
            '    Redis_client_longest_output_list "gauge"\n'
            '    Redis_client_biggest_input_buf "gauge"\n'
            '    Redis_blocked_clients "gauge"\n'
            '    Redis_expired_keys "counter"\n'
            '    Redis_evicted_keys "counter"\n'
            '    Redis_rejected_connections "counter"\n'
            '    Redis_used_memory "bytes"\n'
            '    Redis_used_memory_rss "bytes"\n'
            '    Redis_used_memory_peak "bytes"\n'
            '    Redis_used_memory_lua "bytes"\n'
            '    Redis_mem_fragmentation_ratio "gauge"\n'
            '    Redis_changes_since_last_save "gauge"\n'
            '    Redis_instantaneous_ops_per_sec "gauge"\n'
            '    Redis_rdb_bgsave_in_progress "gauge"\n'
            '    Redis_total_connections_received "counter"\n'
            '    Redis_total_commands_processed "counter"\n'
            '    Redis_total_net_input_bytes "counter"\n'
            '    Redis_total_net_output_bytes "counter"\n'
            '    Redis_keyspace_hits "derive"\n'
            '    Redis_keyspace_misses "derive"\n'
            '    Redis_latest_fork_usec "gauge"\n'
            '    Redis_connected_slaves "gauge"\n'
            '    Redis_repl_backlog_first_byte_offset "gauge"\n'
            '    Redis_master_repl_offset "gauge"\n')

        slave_metrics = (
            '    #Slave-Only'
            '    Redis_master_last_io_seconds_ago "gauge"\n'
            '    Redis_slave_repl_offset "gauge"\n')

        utils.print_step(
            'Begin configuring Redis python plugin for collectd')

        # create directory if it doesn't exist
        if not utils.check_path_exists(python_plugin_path):
            utils.print_step(
                '  Creating directory {} '
                'for collectd python plugin'.format(python_plugin_path))
            res = utils.call_command(
                'mkdir -p {}'.format(python_plugin_path))
            if res == 0:
                utils.print_success()
            else:
                utils.print_failure()
                raise Exception('Unable to create directory.')
                
        utils.print_step(
            '  Moving python plugin')
        res = utils.call_command(
            'cp {src} {dst}'.format(
                src=plugin_src, dst=python_plugin_path))
        if res == 0:
            utils.print_success()
        else:
            utils.print_failure()
            raise Exception('Failed to move the plugin.')
            
        utils.print_step('Begin writing redis configuration for collectd')
        # pull comment and append to it
        if not self.pull_comment(out):
            utils.print_warn('Failed to pull comment.')

        out.write('\n\n')
        out.write(
            '<LoadPlugin python>\n'
            '  Globals true\n'
            '</LoadPlugin>\n\n'
            '<Plugin python>\n'
            '  ModulePath "{path}"\n'
            '  Import "redis_info"\n'.format(path=python_plugin_path))

        while utils.ask('Would you like to add a server to monitor?'):
            iname = utils.prompt_and_check_input(
                prompt=(
                    '\nHow would you like to name this monitoring instance?\n'
                    '(How it should appear on your wavefront metric page, \n'
                    'space between words will be removed)'),
                check_func=(
                    lambda x: x.replace(" ", "") not in iname_list),
                usage=(
                    '{} has already been used.'.format),
                usage_fmt=True).replace(" ", "")

            host = utils.prompt_and_check_input(
                prompt=(
                    'Please enter the hostname that connects to your\n'
                    'redis server: (ex: localhost)'),
                check_func=utils.hostname_resolves,
                usage='{} does not resolve.'.format,
                usage_fmt=True)

            port = utils.prompt_and_check_input(
                prompt=(
                    'What is the TCP-port used to connect to the host? '),
                check_func=utils.check_valid_port,
                usage=(
                    'A valid port is a number '
                    'between (0, 65535) inclusive.\n'),
                default='6379')

            if (host, port) in server_list:
                utils.eprint(
                    'You have already monitored {host}:{port}.'.format(
                        host=host, port=port))
                continue

            plugin_instance = (
                '    Instance "{iname}"\n'
                '    Host "{host}"\n'
                '    Port "{port}"\n').format(
                    iname=iname,
                    host=host, port=port)

            if utils.ask(
                    'Is there an authorization password set up for\n'
                    '{host}:{port}'.format(host=host, port=port),
                    default=None):
                auth = utils.get_input(
                    'What is the authorization password?')
                plugin_instance += (
                    '    Auth "{auth}"\n'.format(auth=auth))

            slave = utils.ask(
                'Is this a slave server?', default='no')

            utils.cprint()
            if slave:
                utils.cprint('(slave server)')
            utils.cprint('Result: \n{}'.format(plugin_instance))
            res = utils.ask('Is the above information correct?')

            if res:
                utils.print_step('Saving instance')
                count = count + 1
                iname_list.append(iname)
                server_list.append((host, port))
                out.write(
                    '\n  <Module redis_info>\n'
                    '{plugin_instance}'
                    '{metrics}'.format(
                        plugin_instance=plugin_instance,
                        metrics=metrics))
                if slave:
                    out.write(slave_metrics)
                out.write('  </Module>\n')
                utils.print_success()
            else:
                utils.cprint('This instance is not saved.')
        out.write('</Plugin>\n')
        return count

    def pull_comment(self, out):
        res = True
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
                    out.write(line)
        except (IOError, OSError) as e:
            utils.eprint('Cannot open file at {}'.format(filepath))
            res = False

        return res

if __name__ == '__main__':
    redis = RedisInstaller(
        'DEBIAN', 'python', 'wavefront_redis.conf')
    config.INSTALL_LOG = '/dev/null'
    redis.install()
