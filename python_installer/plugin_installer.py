import install_utils as utils
import config
import plugin_exception as ex


class PluginInstaller(object):
    """
    The interface for installers

    The following methods need to be implemented
      title():
          - the ascii art for the installer
      overview():
          - general description about what the installer does
      check_depedency()
          - check plugin and installer's dependency
      write_plugin():
          - write the actual plugin file
    """
    def __init__(self, os, plugin_name, conf_name):
        self.os = os
        self.plugin_name = plugin_name
        self.conf_name = conf_name

    # methods that subclass needs to implement
    def title(self):
        raise NotImplementedError()

    def overview(self):
        raise NotImplementedError()

    def check_dependency(self):
        raise NotImplementedError()

    def write_plugin(self, out):
        raise NotImplementedError()

    # helper methods
    def get_conf_name(self):
        return self.conf_name

    def raise_error(self, msg):
        raise ex.MissingDependencyError(msg)

    def check_plugin(self):
        """
        check if the .so file of plugin exists in the following dir
        """

        utils.print_step(
            'Checking if the plugin is installed with '
            'the default collectd package')

        plugin_dir = ''
        if self.os == config.REDHAT:
            plugin_dir = '/usr/lib64/collectd'
        elif self.os == config.DEBIAN:
            plugin_dir = '/usr/lib/collectd'

        if not utils.check_path_exists(plugin_dir):
            raise Exception(
                'Collectd plugin directory is '
                'not found at {}'.format(plugin_dir))

        plugin_mod = self.plugin_name + '.so'
        if utils.check_path_exists(
          '{}/{}'.format(plugin_dir, plugin_mod)):
            utils.print_success()
        else:
            self.raise_error('Missing {} plugin for collectd'.format(
                self.plugin_name))

    def clean_plugin_write(self):
        """
        Prevent unfinished config file from being written into the directory

        Create and write to a temporary file.  Use try catch block to call
        write_plugin function.  If the configuration file is written
        successfully, then it will be copied over to the correct place.
        """
        temp_file = 'wavefront_temp_{0}.conf'.format(utils.random_string(7))
        out = utils.write_file(temp_file)
        error = False
        if out is None:
            utils.exit_with_message('')

        try:
            res = self.write_plugin(out)
        except KeyboardInterrupt as k:
            error = True
            raise k
        except Exception as e:
            utils.eprint(
                'Error: {}\n'
                'Unexpected flow.'.format(e))
            error = True
        finally:
            out.close()
            if error:
                utils.eprint('Closing and removing temp file.\n')
                utils.call_command('rm ' + temp_file)
                raise KeyboardInterrupt

        # if there was at least one instance being monitor
        if res:
            utils.print_step('Copying the plugin file to the correct place')
            cp_cmd = (
                'cp {infile} {conf_dir}/{outfile}').format(
                    infile=temp_file,
                    conf_dir=config.COLLECTD_CONF_DIR,
                    outfile=self.conf_name)
            ret = utils.call_command(cp_cmd)

            if ret == 0:
                utils.print_success()
                utils.cprint(
                    '{} plugin has been written successfully.'.format(
                      self.plugin_name))
                utils.cprint(
                    '{0} can be found at {1}.'.format(
                        self.conf_name,
                        config.COLLECTD_CONF_DIR))
            else:
                utils.call_command('rm {}'.format(temp_file))
                utils.exit_with_message('Failed to copy the plugin file.\n')
        else:
            utils.cprint('You did not provide any instance to monitor.\n')

        utils.call_command('rm {}'.format(temp_file))

    def install(self):
        try:
            self.title()
            self.overview()
            self.check_plugin()
            self.check_dependency()
            self.clean_plugin_write()
        except KeyboardInterrupt:
            utils.eprint(
                'Quitting {}.'.format(
                    self.__class__.__name__))
            return False
        except ex.MissingDependencyError as e:
            utils.eprint(
                'MissingDependencyError: {}\n'
                '{} requires the missing dependency '
                'to continue the installation.'.format(
                    e, self.__class__.__name__))
            return False
        except Exception as e:
            utils.eprint(
                'Error: {}\n'
                '{} was not installed successfully.'.format(
                    e, self.__class__.__name__))
            return False

        utils.print_color_msg('{} was installed successfully.'.format(
            self.__class__.__name__), utils.GREEN)
        return True
