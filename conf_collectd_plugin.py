import install_utils as utils

def check_install_state(plugin):
    print ("Cannot check %s yet." % plugin)
    return False

def write_tcpconns_conf_plugin(open_ports):
    """
    TODO:
    -need to check if tcpconn plugin's dependencies are installed
    -include RemotePort for outbounds connections
        i.e. the servers we are connecting to
    """
    try:
        out = open("10-tcpconns.conf", "w")
    except:
        sys.stderr.write("Unable to write tcpcons.conf file\n")
        sys.exit()
   
    out.write('LoadPlugin tcpconns')
    out.write('<Plugin "tcpconns">\n')
    out.write('  ListeningPorts false\n')
    for port in open_ports:
        out.write('  LocalPort "%d"\n' % port)

    # no remote port yet
    out.write('</Plugin>\n')
    out.close()


def conf_apache_plugin():
    print "---Apache---"
    install = check_install_state("Apache")
    if not install:
        print "This script has detected that you have apache installed and running."
        res = utils.ask("Would you like collectd to collect data from apache")
    else:
        print "You have previously installed this plugin."
        res = utils.ask("Would you like to reinstall this plugin", no)

    if not res:
        return

    # pull the appropriate template

def write_apache_plugin():
    out = utils.file_append("10-apache.conf")

    out.write('LoadPlugin "apache"')
    out.write('<Plugin "apache">\n')
    out.write('

    out.write('</Plugin>\n')
    out.close()
   

if __name__ == "__main__":
    print "Testing conf_collected_plugin"
    conf_apache_plugin()
