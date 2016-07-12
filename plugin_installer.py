import install_utils as utils


COLLECTD_HOME = '/etc/collectd'
COLLECTD_CONF_DIR = COLLECTD_HOME + '/managed_config'


class PluginInstaller():
    """
    The interface for installers


    """
    def title(self):
        raise NotImplementedError()  

    def overview(self):
        raise NotImplementedError()  

    def check_dependency(self):
        raise NotImplementedError()  

    def write_plugin(self, out):
        raise NotImplementedError()  

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
        except:
            utils.eprint('Unexpected flow.')
            error = True
        finally:
            out.close()
            if error:
                utils.eprint('Closing and removing temp file.\n')
                utils.call_command('rm ' + temp_file)
                utils.exit_with_message('')

        # if there was at least one instance being monitor
        if res:
            utils.print_step('Copying the plugin file to the correct place')
            cp_cmd = (
                'cp {infile} {conf_dir}/{outfile}').format(
                    infile=temp_file,
                    conf_dir=COLLECTD_CONF_DIR,
                    outfile=self.conf_name)
            ret = utils.call_command(cp_cmd)

            if ret == 0:
                utils.print_success()
                utils.cprint('MySQL plugin has been written successfully.')
                utils.cprint(
                    '{0} can be found at {1}.'.format(self.conf_name,
                        COLLECTD_CONF_DIR))
            else:
                utils.call_command('rm {}'.format(temp_file))
                utils.exit_with_message('Failed to copy the plugin file.\n')
        else:
            utils.cprint('You did not provide any instance to monitor.\n')

        utils.call_command('rm {}'.format(temp_file))

    def install(self):
        self.title()
        self.overview()
        self.check_dependency()
        self.clean_plugin_write()
