import re

import common.install_utils as utils
import common.config as config
import plugin_dir.utils.plugin_utils as p_utils


def title():
    utils.cprint(
        ' ****     **         **                 \n'
        '/**/**   /**  ***** //                  \n'
        '/**//**  /** **///** ** *******  **   **\n'
        '/** //** /**/**  /**/**//**///**//** ** \n'
        '/**  //**/**//******/** /**  /** //***  \n'
        '/**   //**** /////**/** /**  /**  **/** \n'
        '/**    //***  ***** /** ***  /** ** //**\n'
        '//      ///  /////  // ///   // //   // \n')


def overview():
    utils.cprint()
    utils.cprint(
        'To collect metrics from Nginx server, the following\n'
        'steps need to be taken:\n'
        '1. http_stub_status_module for nginx needs to be enabled.\n'
        '2. Enable the nginx-status page for each virtual host.\n')

    _ = utils.cinput('Press Enter to continue')


def check_dependency():
    utils.print_step('Checking dependency')
    utils.print_step('  Checking http_stub_status_module')

    cmd_res = utils.get_command_output(
        'nginx -V 2>&1 | grep -o '
        'with-http_stub_status_module')
    if cmd_res is None:
        utils.print_warn(
            'http_stub_status_module is not enabled.\n'
            'This module is required to enable the '
            'nginx-status page.')
        self.raise_error('http_stub_status_module')
    utils.print_success()


def check_server_url(url, url_list=[]):
    """
    check if the url provided is a valid server-status page

    Input:
        url string: the url provided by the user
        url_list []string: list of url user has monitored already
    Output:
        ret_val bool:
            True if user provides a valid url
            False otherwise
    """
    ret_val = False

    if not p_utils.check_url(url, url_list):
        return False

    res = utils.get_command_output('curl -s {url}'.format(url=url))
    status = check_nginx_status(res)
    if not status:
        utils.print_warn(
            'The url you have provided '
            'does not seem to be the correct server_status '
            'page.  Incorrect server-status will not be '
            'recorded.')
        record = utils.ask(
            'Would you like to record this url anyway?', 'no')
        if record:
            ret_val = True
    else:
        ret_val = True

    return ret_val


def check_nginx_status(payload):
    """
    Loose regex check on the content of the page
    """
    nginx_re = re.search(
        r'active connections:\s*\d+\s*'
        'server accepts handled requests', payload, re.I)
    nginx_re2 = re.search(
        r'reading: \d+ writing: \d+ waiting: \d+', payload, re.I)

    if nginx_re is None or nginx_re2 is None:
        return False

    return True


def plugin_usage():
    utils.cprint(
      'To monitor a nginx server, '
      'you must enable a server-status page.\n'
      'To enable a server-status page, the following code in quote\n'
      '"location /server-status{\n'
      '  stub_status on;\n'
      '  access_log off;\n'
      '  allow 127.0.0.1;\n'
      '  deny all;\n'
      '}"\n'
      'must be included within a server block '
      'for the .conf file of your server.\n\n'
      'To check whether the server-status page is working, '
      'please visit\n'
      '\tyour-server-name/server-status\n')

if __name__ == '__main__':
    utils.print_step('Testing module {}'.format(__loader__.fullname))
    utils.cprint(get_sample_config('nginx'))
