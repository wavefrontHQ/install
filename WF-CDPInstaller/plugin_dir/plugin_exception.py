import common.install_utils as utils


class MissingDependencyError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


if __name__ == '__main__':
    utils.cprint('begin testing plugin exception')
    raise Exception('Missing dependency')
