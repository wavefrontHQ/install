#!/usr/bin/env python

from distutils.core import setup

setup(
    name='WF-PCInstaller',
    version='1.0.0dev',
    description='Python Configuration Installer',
    scripts=['python_installer/gather_metrics.py'],
    packages=[
        'python_installer', 'plugin_dir', 'common',
        'plugin_conf', 'plugin_extension'],
    package_data={
        'python_installer': ['config/*.json'],
        'plugin_conf': ['*.conf'],
        'plugin_extension': ['*.py'],
        'plugin_dir': ['collectd/*.py'],
        'plugin_dir': ['telegraf/*.py']}
    )
