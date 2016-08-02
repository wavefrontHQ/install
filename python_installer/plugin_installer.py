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
        self.plugin_dir = 'NOT SET'
        if self.os == config.REDHAT:
            self.plugin_dir = '/usr/lib64/collectd'
        elif self.os == config.DEBIAN:
            self.plugin_dir = '/usr/lib/collectd'

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
    def raise_error(self, msg):
        raise ex.MissingDependencyError(msg)

    def check_plugin(self):
        """
        check if the .so file of plugin exists in the following dir
        """

        utils.print_step(
            'Checking if the plugin is installed with '
            'the default collectd package')

        if not utils.check_path_exists(self.plugin_dir):
            raise Exception(
                'Collectd plugin directory is '
                'not found at {}'.format(self.plugin_dir))

        plugin_mod = self.plugin_name + '.so'
        if utils.check_path_exists(
          '{}/{}'.format(self.plugin_dir, plugin_mod)):
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
        error = None

        try:
            with open(temp_file, 'w') as out:
                try:
                    res = self.write_plugin(out)
                except KeyboardInterrupt as e:
                    error = e
                except Exception as e:
                    error = e
                finally:
                    if error:
                        utils.eprint('\nClosing and removing temp file.\n')
                        utils.call_command('rm ' + temp_file)
                        raise error
        except (IOError, OSError) as e:
            utils.eprint('Cannot open {}'.format(filepath))
            raise Exception(
                  'Error: {}\n'
                  'Cannot open {}.'.format(e, filepath))

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
                raise Exception('Failed to copy the plugin file.\n')
        else:
            utils.call_command('rm {}'.format(temp_file))
            raise Exception('You did not provide any instance to monitor.\n')

        utils.call_command('rm {}'.format(temp_file))

    def install(self):
        class_name = self.__class__.__name__
        try:
            self.title()
            self.overview()
            self.check_plugin()
            self.check_dependency()
            self.clean_plugin_write()
        except KeyboardInterrupt as e:
            utils.eprint(
                'Quitting {}.'.format(
                    class_name))
            utils.append_to_log(e, config.INSTALL_LOG)
            return False
        except ex.MissingDependencyError as e:
            utils.eprint(
                'MissingDependencyError: {}\n'
                '{} requires the missing dependency '
                'to continue the installation.'.format(
                    e, class_name))
            utils.append_to_log(e, config.INSTALL_LOG)
            return False
        except Exception as e:
            utils.eprint(
                'Error: {}\n'
                '{} was not installed successfully.'.format(
                    e, class_name))
            utils.append_to_log(e, config.INSTALL_LOG)
            return False

        utils.print_color_msg('{} was installed successfully.'.format(
            class_name), utils.GREEN)
        return True
