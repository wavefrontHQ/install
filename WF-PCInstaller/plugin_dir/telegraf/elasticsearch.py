"""
Tested with elasticsearch 2.3.5 (Ubuntu 14.04)
"""
import common.install_utils as utils
import plugin_dir.plugin_installer as inst
import common.config as config
import plugin_dir.utils.plugin_utils as p_utils
import plugin_dir.telegraf.telegraf_utils as tf_utils


class ElasticsearchConfigurator(inst.PluginInstaller):
    def title(self):
        utils.cprint(
            " _____ _           _   _      _____                     _     \n"
            "|  ___| |         | | (_)    /  ___|                   | |    \n"
            "| |__ | | __ _ ___| |_ _  ___\ `--.  ___  __ _ _ __ ___| |__  \n"
            "|  __|| |/ _` / __| __| |/ __|`--. \/ _ \/ _` | '__/ __| '_ \ \n"
            "| |___| | (_| \__ \ |_| | (__/\__/ /  __/ (_| | | | (__| | | |\n"
            "\____/|_|\__,_|___/\__|_|\___\____/ \___|\__,_|_|  \___|_| |_|\n")

    def overview(self):
        utils.cprint()
        utils.cprint(
            'The elasticsearch plugin queries endpoints to obtain\n'
            'node and optionally cluster stats.\n'
            'The enable the plugin, it needs\n'
            'hostname and the port to connect\n'
            'to the elasticsearch server.\n')

        _ = utils.cinput('Press Enter to continue')
        utils.print_step('Begin telegraf Elasticsearch plugin installer')

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
            (host, port) = p_utils.get_host_and_port(def_port='9200')
            if (host, port) in server_list:
                utils.eprint(
                    'You have already added this {host}:{port}.'.format(
                        host=host, port=port))
                continue

            plugin_instance = (
                '    Host "{host}"\n'
                '    Port "{port}"\n').format(
                    host=host, port=port)

            utils.cprint()
            utils.cprint('Result: \n{}'.format(plugin_instance))
            res = utils.ask('Is the above information correct?')

            if res:
                utils.print_step('Saving instance')
                server_list.append((host, port))
                data['servers'].append(
                    'http://{host}:{port}'.format(
                        host=host, port=port))
                utils.print_success()
            else:
                utils.cprint('This instance is not saved.')

        return data

    def output_config(self, data, out):
        utils.print_step(
            'Begin writing telegraf elasticsearch configuration')
        server_list = data['servers']
        count = len(server_list)
        if not count:
            return False

        conf = tf_utils.get_sample_config('elasticsearch')
        if conf is None:
            raise Exception(
                'Cannot obtain sample config with telegraf command')

        server_list_str = p_utils.json_dumps(server_list)

        res = tf_utils.edit_conf(
            conf, 'servers', server_list_str)

        out.write(res)
        return True

if __name__ == '__main__':
    es = ElasticsearchConfigurator(
        'DEBIAN', 'TELEGRAF', 'elasticsearch', 'wavefront_elasticsearch.conf')
    config.INSTALL_LOG = '/dev/stdout'
    es.install()
