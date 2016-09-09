# install script will pass in the name of log file
INSTALL_LOG = None
DEBUG = True
OPERATING_SYSTEM = None
AGENT = None
APP_DIR = 'NOTSET'
# using variable so checking for typo is easier
DEBIAN = 'DEBIAN'
REDHAT = 'REDHAT'
COLLECTD = "COLLECTD"
TELEGRAF = "TELEGRAF"
INSTALL_STATE_FILE = 'install_state.json'
TEST = False


# collectd
COLLECTD_HOME = '/etc/collectd'
COLLECTD_CONF_DIR = COLLECTD_HOME + '/managed_config'
COLLECTD_INSTALL_STATE_FILE_PATH = '{}/{}'.format(
    COLLECTD_CONF_DIR, INSTALL_STATE_FILE)
COLLECTD_PLUGIN_DIR = 'plugin_dir/collectd'
COLLECTD_PYTHON_PLUGIN_PATH = '/opt/collectd/plugins/python'
COLLECTD_PLUGIN_TEST_DIR = COLLECTD_PLUGIN_DIR + '/test'


# telegraf
TELEGRAF_HOME = '/etc/telegraf'
TELEGRAF_CONF_DIR = TELEGRAF_HOME + '/telegraf.d'
TELEGRAF_INSTALL_STATE_FILE_PATH = '{}/{}'.format(
    TELEGRAF_CONF_DIR, INSTALL_STATE_FILE)
TELEGRAF_PLUGIN_DIR = 'plugin_dir/telegraf'


# python installer vars
PLUGINS_FILE = 'support_plugins.json'
PLUGINS_FILE_PATH = 'python_installer/config/' + PLUGINS_FILE
PLUGIN_CONF_DIR = 'plugin_conf'
PLUGIN_EXTENSION_DIR = 'plugin_extension'
