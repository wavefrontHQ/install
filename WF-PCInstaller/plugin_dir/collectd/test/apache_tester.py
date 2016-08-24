import common.install_utils as utils
import common.config as config
import plugin_dir.collectd.apache as a_inst


class ApacheInstallerTest(a_inst.ApacheInstaller):
    def title(self):
        pass

    def overview(self):
        pass

    def check_dependency(self):
        pass

    def collect_data(self):
        """
        data = {
            "instance_name": "url",
        }
        """
        data = {
            "docker_test": "http://localhost/server-status"
        }
        return data
 
    def output_config(self, data, out):
        utils.print_step('Begin writing apache plugin for collectd')
        if not data:
            return False

        out.write(
            'LoadPlugin "apache"\n'
            '<Plugin "apache">\n')

        for instance in data:
            out.write(
                '  <Instance "{instance}">\n'
                '    URL "{url}"\n'
                '  </Instance>\n'.format(instance=instance,
                                          url=data[instance]))

        out.write('</Plugin>\n')
        return True

if __name__ == '__main__':
    apache = ApacheInstallerTest(
        'DEBIAN', 'COLLECTD', 'apache', 'wavefront_apache.conf')
    config.INSTALL_LOG = '/dev/stdout'
    apache.install()
