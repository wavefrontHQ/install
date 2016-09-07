# Wavefront Python Configuration Installer

##Usage:
```
python -m python_installer.gather_metrics \
[operating system(DEBIAN|REDHAT)] \
[agent(COLLECTD|TELEGRAF)] [APP_DIR] [log file] [-TEST]
```
    operating system:
        Determines the installer control flow.
    agent:
        Determines the directory path.
    app_dir:
        The location of WF-PCInstaller where setup.py resides.
    log_file:
        Errors will log to this file.
    --TEST:
        Installs all detected applications with default setting.
        This is for integeration test.  Default is off.

##Package map:

The structure of this directory

    common/
        contains common installation utilities (install_utils.py) 
        and global variables (common.py).
    plugin_conf/
        base configuration files used for some collectd plugins.
    plugin_extension/
        extension files made using collectd plugin.
    python_installer/
        main script (gather_metrics.py) resides here.
    python_dir/
        contains interface for configurator class (plugin_installer.py).
        configurator classes reside here. 
    collectd/
        contains collectd configurators.
    telegraf/
        contains telegraf configurators.
    utils/
        common utils shared among telegraf and collectd.
    setup.py
        can be used to package the PCI via the sdist option.
    MANIFEST.in
        specify what files to include in the tar


## Updating package
```
python setup.py sdist
```
Before updating the python zip file in release, please check
whether the appropriate files are packaged in MANIFEST.

To generate a MANIFEST file.
```
python setup.py sdist --manifest-only
```
