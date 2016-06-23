import socket
import sys
from datetime import datetime
import cProfile
import subprocess

def port_scan(host, port):
    """
    Using ipv4, TCP connection to test whether a port is
    being used.
    """
    # AF_INET specifies ipv4, SOCK_STREAM for TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock.connect((host, port))
    except socket.error:
        return False
    except KeyboardInterrupt:
        print "Scanning interrupted"
        sys.exit()
    except socket.gaierror:
        print "Hostname could not be resolved"
        sys.exit()
    else:
        return port
    finally:
        sock.close()

def detect_used_ports():
    """
    Scan through localhost 0-1024 ports
    """
    MAX_PORT = 1025
    DEFAULT_HOST = '127.0.0.1'
    open_ports = []
    socket.setdefaulttimeout(1)
    for port in range(0, MAX_PORT):   
        res = port_scan(DEFAULT_HOST, port)
        if( res != False ):
            open_ports.append(port)
        # debugging purpose to see if program is running
        if( port % 5000 == 0 and port != 0 ):
            sys.stderr.write(".") 
    return open_ports

def write_tcpconns_conf(open_ports):
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

def detect_applications():
    output = subprocess.check_output(['ps'], '-A')
    if 'Httpd' in output:
        print("Httpd is up and running!")


if __name__ == "__main__":
    print "Begin port scanning"
    t1 = datetime.now()
    #cProfile.run("detect_used_ports()")
    #print (detect_used_ports())
    write_tcpconns_conf(detect_used_ports())
    t2 = datetime.now()
    print "Time took: ", (t2-t1)
