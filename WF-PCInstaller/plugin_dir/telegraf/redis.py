"""
redis-server 2.8.4 (Ubuntu 14.04)
"""
import common.install_utils as utils
import common.config as config
import plugin_dir.plugin_installer as inst
import plugin_dir.utils.plugin_utils as p_utils
import plugin_dir.telegraf.telegraf_utils as tf_utils


class RedisConfigurator(inst.PluginInstaller):
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
            'The telegraf redis plugin connects to one or more\n'
            'Redis servers and gathers information\n'
            'about their states.\n'
            'To enable this plugin, hostname and port\n'
            'will be needed to connect to redis-server.\n')

        _ = utils.cinput('Press Enter to continue')
        utils.print_step('Begin telegraf redis plugin installer')

    def check_dependency(self):
        pass 

    def collect_data(self):
        """
        data = {
            servers: []
        }
        """
        data = {
            'servers': []
        }
        server_list = []

        while utils.ask('\nWould you like to add a server to monitor?'):
            (host, port) = p_utils.get_host_and_port(def_port='6379')
            if (host, port) in server_list:
                utils.eprint(
                    'You have already added this {host}:{port}.'.format(
                        host=host, port=port))
                continue

            plugin_instance = (
                '    Host "{host}"\n'
                '    Port "{port}"\n').format(
                    host=host, port=port)

            protected = utils.ask(
                    'Is there an authorization password set up for\n'
                    '{host}:{port}'.format(host=host, port=port),
                    default=None)
            if protected:
                auth = utils.get_input(
                    'What is the authorization password?')
                plugin_instance += (
                    '    Auth "{auth}"\n'.format(auth=auth))

            utils.cprint()
            utils.cprint('Result: \n{}'.format(plugin_instance))
            res = utils.ask('Is the above information correct?')

            if res:
                utils.print_step('Saving instance')
                server_list.append((host, port))
                if protected:
                    url = (
                        ':{auth}@{host}:{port}').format(
                            auth=auth,
                            host=host,
                            port=port)
                else:
                    url = (
                        '{host}:{port}').format(
                            host=host, port=port)
                data['servers'].append(url)
                utils.print_success()
            else:
                utils.cprint('This instance is not saved.')

        return data

    def output_config(self, data, out):
        utils.print_step('Begin writing telegraf redis configuration')
        server_list = data['servers']
        count = len(server_list)
        if not count:
            return False

        conf = tf_utils.get_sample_config('redis')
        if conf is None:
            raise Exception(
                'Cannot obtain sample config with telegraf command')

        server_list_str = p_utils.json_dumps(server_list)
          
        res = tf_utils.edit_conf(
            conf, 'servers', server_list_str)

        out.write(res)
        return True

if __name__ == '__main__':
    redis = RedisConfigurator(
        'DEBIAN', 'TELEGRAF', 'python', 'wavefront_redis.conf')
    config.INSTALL_LOG = '/dev/stdout'
    redis.install()
