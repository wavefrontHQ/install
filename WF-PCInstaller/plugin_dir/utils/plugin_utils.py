"""
- contains common functions from plugins that can be
factored out.
- contains prompts and error messages.
"""
import common.install_utils as utils
import json


# common methods extraced out from other plugins
def check_url(url, url_list=[]):
    """
    check if the url provided is a valid url

    Input:
        url string: the url provided by the user
        url_list []string: list of url user has monitored already
    Output:
        True if the user provides a valid url
        False otherwise
    """
    if url is None:
        return False

    if not utils.check_url_scheme(url):
        utils.print_color_msg(
            '\nPlease provide the url scheme.',
            utils.YELLOW)
        return False

    # check repeat
    if url in url_list:
        utils.eprint(
            'You have already added this {}'.format(url))
        return False

    if not check_http_response(url):
        return False
    
    return True


def check_http_response(url):
    """
    check if the url is a valid

    Input:
        url string: the url provided by the user
    Output:
        ret_val bool:
            True if the url is valid and returns 200 OK
            False otherwise
    """
    ret_val = False
    utils.print_step('Checking http response for {url}'.format(url=url))
    res = utils.get_command_output('curl -s --head {url}'.format(url=url))

    if res is None:
        ret_code = utils.INVALID_URL
    else:
        ret_code = utils.get_http_return_code(res)

    if ret_code == utils.NOT_AUTH:
        # skip for this case for now, ask for user/pass
        utils.print_failure()
        utils.eprint(
            'Authorization is required, please '
            'try again.\n')
    elif ret_code == utils.NOT_FOUND or ret_code == utils.INVALID_URL:
        utils.print_failure()
        utils.eprint(
            'Invalid url was provided, please try '
            'again.\n')
    elif ret_code == utils.HTTP_OK:
        utils.print_success()
        ret_val = True

    return ret_val
    
    
def get_server_status_list(check_server_url):
    """
    get a list of server-status urls

    Input:
        check_server_url(string, []string) bool
          - a function takes a url string and a list of urls
            and return whether the url is valid
    Output:
        server_list []string: list of valid urls
    """
    server_list = []

    while utils.ask('Would you like to add a server to monitor?'):
        url = None
        while not check_server_url(url, server_list):
            url = utils.get_input(
                'Please enter the url that contains your '
                'server-status\n'
                '(ex: http://localhost/server-status):')

        utils.cprint()
        utils.cprint(
            'URL: {}'.format(url))
        res = utils.ask(
            'Is this the correct url?')
        if res:
            utils.print_step('Saving instance')
            server_list.append(url)
            utils.print_success()
        else:
            utils.cprint('Instance is not saved.')

    return server_list


def get_host_and_port(def_host='127.0.0.1', def_port=None):
    """
    prompt for host and port

    Input:
        def_host string:
            sample host
        def_port string:
            port numbers
    Output: tuple of result (host, port)
    """
    host = utils.prompt_and_check_input(
        prompt=(
            '\nPlease enter the hostname that connects to your '
            'server:'),
        check_func=utils.hostname_resolves,
        usage='{} does not resolve.'.format,
        usage_fmt=True,
        default=def_host)

    port = utils.prompt_and_check_input(
        prompt=(
            '\nWhat is the TCP-port used to connect to the host?'),
        check_func=utils.check_valid_port,
        usage=(
            'A valid port is a number '
            'between (0, 65535) inclusive.\n'),
        default=def_port)

    return (host, port)


# other helpers
def json_dumps(obj):
    """
    return str output of json.dumps

    reason: have a single import statement in this module
    """
    return json.dumps(obj)
