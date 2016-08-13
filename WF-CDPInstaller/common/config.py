# install script will pass in the name of log file
INSTALL_LOG = None
DEBUG = False
OPERATING_SYSTEM = None
DEBIAN = 'DEBIAN'
REDHAT = 'REDHAT'
# installation path
COLLECTD_HOME = '/etc/collectd'
COLLECTD_CONF_DIR = COLLECTD_HOME + '/managed_config'
PLUGIN_CONF_DIR = 'plugin_conf'
PLUGIN_EXTENSION_DIR = 'plugin_extension'
APP_DIR = '/tmp/WF-CDPInstaller'
# Install state path and name
INSTALL_STATE_FILE = 'install_state.json'
INSTALL_STATE_FILE_PATH = '{}/{}'.format(
    COLLECTD_CONF_DIR, INSTALL_STATE_FILE)
# others
PLUGINS_FILE = 'support_plugins.json'
PLUGINS_FILE_PATH = 'python_installer/config/' + PLUGINS_FILE
