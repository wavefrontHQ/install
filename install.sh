#!/bin/bash
# Install Wavefront Proxy and configures standard collectd plugin
# ####

function logo() {
    cat << "EOT"
 __      __                     _____                      __   
/  \    /  \_____ ___  __ _____/ ____\______  ____   _____/  |_ 
\   \/\/   /\__  \\  \/ // __ \   __\\_  __ \/  _ \ /    \   __\
 \        /  / __ \\   /\  ___/|  |   |  | \(  <_> )   |  \  |  
  \__/\  /  (____  /\_/  \___  >__|   |__|   \____/|___|  /__|  
       \/        \/          \/                         \/      
EOT
}

function usage() {
    echo
    echo "USAGE"
    echo "====="
    echo "install.sh [ --proxy | --collectd | --server <server_url> | --token <token> | --proxy_address <proxy_address> | --proxy_port <port> | --overwrite_collectd_config | --app_configure ]"
    echo
    echo "    --proxy"
    echo "          Installs the Wavefront Proxy"
    echo "    --server <server_url>"
    echo "          The URL for the Wavefront cluster that data should be sent to."
    echo "    --token <token>"
    echo "          The token to register the agent. Must have agent management permissions"
    echo
    echo "    --collectd"
    echo "          Installs collectd and configures standard metric collection"
    echo "    --proxy_address <proxy_address>"
    echo "          The address of the proxy to send data to."
    echo "    --proxy_port <port>"
    echo "          The proxy port to send collectd data to."
    echo "    --overwrite_collectd_config"
    echo "          Overwrite existing collectd configurations in /etc/collectd/"
    echo "    --app_configure"
    echo "          Launch the interactive collectd plugins installer"
    echo
}

# Input arguments
INSTALL_PROXY=""
INSTALL_COLLECTD=""
ALLOW_HTTP=""
SERVER=""
TOKEN=""
PROXY=""
PROXY_PORT=""
OVERWRITE_COLLECTD_CONFIG=""
APP_FINISHED=""
APP_CONFIGURE=""
APP_BASE=wavefront
APP_HOME=/opt/$APP_BASE/$APP_BASE-proxy
CONF_FILE=$APP_HOME/conf/$APP_BASE.conf
COLLECTD_WAVEFRONT_CONF_FILE=/etc/collectd/managed_config/10-wavefront.conf
PACKAGE_CLOUD_DEB="https://packagecloud.io/install/repositories/wavefront/proxy/script.deb.sh"
PACKAGE_CLOUD_RPM="https://packagecloud.io/install/repositories/wavefront/proxy/script.rpm.sh"
COLLECTD_PLUGINS=(
    "disk" "netlink" "apache" "java" "mysql" "nginx" "postgresql" "python")
APP_CONFIGURE_NAME="WF-CDPInstaller-1.0.0dev"

while :
do
    case $1 in
        -h)
            usage
            exit 0
            ;;
        --proxy)
            INSTALL_PROXY="yes"
            shift
            ;;
        --collectd)
            INSTALL_COLLECTD="yes"
            shift
            ;;
        --allow_http)
            ALLOW_HTTP="yes"
            shift
            ;;
        --server)
            SERVER=$2
            shift 2
            ;;
        --token)
            TOKEN=$2
            shift 2
            ;;
        --proxy_address)
            PROXY=$2
            shift 2
            ;;
        --proxy_port)
            PROXY_PORT=$2
            shift 2
            ;;
        --overwrite_collectd_config)
            OVERWRITE_COLLECTD_CONFIG="yes"
            APP_CONFIGURE="yes"
            shift
            ;;
        --app_configure)
            APP_CONFIGURE="yes"
            shift
            ;;
        --log)
            INSTALL_LOG=$2
            shift 2
            ;;
        --next)
            PACKAGE_CLOUD_DEB="https://packagecloud.io/install/repositories/wavefront/proxy-next/script.deb.sh"
            PACKAGE_CLOUD_RPM="https://packagecloud.io/install/repositories/wavefront/proxy-next/script.rpm.sh"
            shift
            ;;
        *)
            if [ -z "$1" ]; then
                break
            else
                echo "Unknown argument: $1"
                usage
                exit 1
            fi
            ;;
    esac
done

function get_input() {
    # get_input <prompt> [ <default_value> ]
    default_value=$2
    if [ -n "$default_value" ]; then
        prompt="$1 (default: $default_value)"
    else
        prompt=$1
    fi
    user_input=""
    while [ -z "$user_input" ]; do
        echo $prompt
        read user_input
        if [ -z "$user_input" ] && [ -n "$default_value" ]; then
            user_input=$default_value
        fi
        if [ -n "$user_input" ]; then
            if [[ $user_input == *","* ]]; then
                error "The value cannot contain commas (,)."
                user_input=""
            fi
        else
            error "The value cannot be blank."
        fi
    done
}

################################################################################
# Terminal output helpers
################################################################################

# echo_title() outputs a title padded by =, in yellow.
function echo_title() {
    TITLE=$1
    NCOLS=$(tput cols)
    NEQUALS=$((($NCOLS-${#TITLE})/2-1))
    EQUALS=$(printf '=%.0s' $(seq 1 $NEQUALS))
    tput setaf 3  # 3 = yellow
    echo "$EQUALS $TITLE $EQUALS"
    tput sgr0  # reset terminal
}

# echo_step() outputs a step collored in cyan, without outputing a newline.
function echo_step() {
    tput setaf 6  # 6 = cyan
    echo -n "$1"
    tput sgr0  # reset terminal
}

# echo_step_info() outputs additional step info in cyan, without a newline.
function echo_step_info() {
    tput setaf 6  # 6 = cyan
    echo -n " ($1)"
    tput sgr0  # reset terminal
}

# echo_right() outputs a string at the rightmost side of the screen.
function echo_right() {
    TEXT=$1
    echo
    tput cuu1
    tput cuf $(tput cols)
    tput cub ${#TEXT}
    echo $TEXT
}

# echo_failure() outputs [ FAILED ] in red, at the rightmost side of the screen.
function echo_failure() {
    tput setaf 1  # 1 = red
    echo_right "[ FAILED ]"
    tput sgr0  # reset terminal
}

# echo_success() outputs [ OK ] in green, at the rightmost side of the screen.
function echo_success() {
    tput setaf 2  # 2 = green
    echo_right "[ OK ]"
    tput sgr0  # reset terminal
}

function echo_warning() {
    tput setaf 3  # 3 = yellow
    echo_right "[ WARNING ]"
    tput sgr0  # reset terminal
    echo "    ($1)"
}

# exit_with_message() outputs and logs a message before exiting the script.
function exit_with_message() {
    echo
    echo $1
    echo -e "\n$1" >>  ${INSTALL_LOG}
    if [[ $INSTALL_LOG && "$2" -eq 1 ]]; then
        echo "For additional information, check the Wavefront install log: $INSTALL_LOG"
    fi
    echo
    debug_variables
    echo
    exit 1
}

# exit_with_failure() calls echo_failure() and exit_with_message().
function exit_with_failure() {
    echo_failure
    exit_with_message "FAILURE: $1" 1
}

# check_if_root_or_die() verifies if the script is being run as root and exits
# otherwise (i.e. die).
function check_if_root_or_die() {
    echo_step "Checking installation privileges"
    echo -e "\nid -u" >>${INSTALL_LOG}
    SCRIPT_UID=$(id -u)
    if [ "$SCRIPT_UID" != 0 ]; then
        exit_with_failure "Installer should be run as root"
    fi
    echo_success
}

################################################################################
# Configuration parameters
################################################################################
REDHAT_REPOSITORY="http://pkg.ci.collectd.org"
REDHAT_PUBLIC_KEY_FILE="pubkey.asc"

################################################################################
# Other helpers
################################################################################

function ask() {
    # http://djm.me/ask
    while true; do
        if [ "${2:-}" = "Y" ]; then
            prompt="Y/n"
            default=Y
        elif [ "${2:-}" = "N" ]; then
            prompt="y/N"
            default=N
        else
            prompt="y/n"
            default=
        fi

        # Ask the question - use /dev/tty in case stdin is redirected from somewhere else
        read -p "$1 [$prompt] " REPLY </dev/tty

        # Default?
        if [ -z "$REPLY" ]; then
            REPLY=$default
        fi

        # Check if the reply is valid
        case "$REPLY" in
            Y*|y*) return 0 ;;
            N*|n*) return 1 ;;
        esac

    done
}

# debug_variables() print all script global variables to ease debugging
debug_variables() {
    echo "ARCHITECTURE: $ARCHITECTURE"
    echo "OPERATING_SYSTEM: $OPERATING_SYSTEM"
    echo "FLAVOR: $FLAVOR/$CODENAME"
}

# check_if_supported() verifies if an operating system $FLAVOR/$CODENAME
# is supported and exits otherwise.
check_if_supported() {
    MESSAGE="$FLAVOR/$CODENAME not yet supported."
    case $FLAVOR in
        Ubuntu)
            case $CODENAME in
                precise|trusty|xenial)
                    ;;
                *)
                    exit_with_failure "$MESSAGE"
                    ;;
            esac
            ;;
        Debian)
            case $CODENAME in
                wheezy|jessie|stretch|buster|7|8|9|10)
                    ;;
                *)
                    exit_with_failure "$MESSAGE"
                    ;;
            esac
            ;;
        CentOS|RHEL)
            case $CODENAME in
                5)
                    ;;
                6)
                    ;;
                7)
                    ;;
                *)
                    exit_with_failure "$MESSAGE"
                    ;;
            esac
            ;;
        AMAZON)
        	case $CODENAME in
        		2015.09|2015.03|2014.09|2016.03)
        			CODENAME=6
        			;;
        		*)
        			exit_with_failure "$MESSAGE"
        			;;
        	esac
        	;;
        *)
            exit_with_failure "$MESSAGE"
            ;;
    esac
}

# command_exists() tells if a given command exists.
function command_exists() {
    hash $1 >/dev/null 2>&1
}

# use the given INSTALL_LOG or set it to a random file in /tmp
function set_install_log() {
    if [[ ! $INSTALL_LOG ]]; then
        command_exists tr || \
            exit_with_failure "Command 'tr' not found. Use --log to set the INSTALL_LOG."
        command_exists head || \
            exit_with_failure "Command 'head' not found. Use --log to set the INSTALL_LOG."
        export INSTALL_LOG="/tmp/install_wavefront_$(< /dev/urandom tr -dc A-Z-a-z-0-9 | head -c${1:-10};echo;).log"
    fi
}

# detect_operating_system() obtains the operating system and exits if it's not
# one of: Ubuntu, RedHat, CentOs.
function detect_operating_system() {
    echo_step "Detecting operating system"
    if [ -f /etc/debian_version ]; then
        echo -e "\ntest -f /etc/debian_version" >>${INSTALL_LOG}
        echo_step_info "Debian/Ubuntu"
        OPERATING_SYSTEM="DEBIAN"
    elif [ -f /etc/redhat-release ] || [ -f /etc/system-release-cpe ]; then
        echo -e "\ntest -f /etc/redhat-release || test -f /etc/system-release-cpe" >>${INSTALL_LOG}
        echo_step_info "RedHat/CentOS"
        OPERATING_SYSTEM="REDHAT"
    else
        echo -e "\ntest -f /etc/debian_version" >>${INSTALL_LOG}
        echo -e "\ntest -f /etc/redhat-release || test -f /etc/system-release-cpe" >>${INSTALL_LOG}
        exit_with_failure "Unsupported operating system"
    fi
    echo_success
    export OPERATING_SYSTEM
}

# detect_architecture() obtains the system architecture and exits if it's not
# one of: i686, x86_64.
function detect_architecture() {
    echo_step "Detecting architecture"
    echo -e "\nuname -m" >>${INSTALL_LOG}
    ARCHITECTURE=$(uname -m); export ARCHITECTURE
    case "$ARCHITECTURE" in
        i386|i486|i586|i686)
            ARCHITECTURE=i386
            ;;
    esac
    if [ "$ARCHITECTURE" == "x86_64" ]; then
        echo_step_info "$ARCHITECTURE"
        echo_success
    else
        exit_with_failure "Unsupported architecture ($ARCHITECTURE)"
    fi
}

# check if the fqdn can be resolved locally
function check_fqdn() {
    echo_step "Checking FQDN"
    echo -e "\nhostname -f" >>${INSTALL_LOG}
    hostname -f >> ${INSTALL_LOG} 2>&1
    if [ "$?" != 0 ]; then
        echo_failure
        echo
        echo -e "\nFDQN needs to be resolved before the installation." >>${INSTALL_LOG}
        echo "FDQN needs to be resolved before the installation."
        echo "Manual change for hosts file (usually /etc/hosts) is required."
        exit_with_message "Failed to resolve FDQN"
    else
        echo_success
    fi
}

# yum_quiet_install() is a helper function that
# that yum install the array of collectd plugins
# $1 - arrayname
function yum_quiet_install() {
    local _aname=$1[@]
    local _array=("${!_aname}")
    for plugin in "${_array[@]}"
    do
        echo -e "\nyum -y -q install collectd-$plugin" >>${INSTALL_LOG}
        yum -y install collectd-$plugin >>${INSTALL_LOG} 2>&1
        if [ "$?" != 0 ]; then
            exit_with_failure "Failed to install collectd-$plugin"
        fi
    done
}


# main()
set_install_log

echo
echo
logo
echo
echo
echo_title "Welcome to Wavefront"
check_if_root_or_die
detect_architecture
detect_operating_system
check_fqdn

if [ -z "$INSTALL_PROXY" ] && [ -z "$INSTALL_COLLECTD" ]; then
    echo
    echo "Beginning interactive installation... (run with -h for flags to enable unattended installation)"
    echo 
    echo "The Wavefront Proxy acts as a relay for collectd, graphite and OpenTSDB telemetry data."
    echo "======================================================================================="
    echo
    echo "By default, it will listen to telemetry data on port 2878 in the following format:"
    echo "		[metric] [value] [timestamp] [annotations]"
    echo "As well as OpenTSDB traffic on port 4242 (\"telnet\" format)"
    echo "		PUT [metric] [timestamp] [value] [annotations]"
    echo
    echo "Additional options are available at $CONF_FILE and"
    echo "can be configured after installation (instructions are provided in the file)."
    echo
    echo "The script will install the proxy using available package managers, updates do not require the "
    echo "use of this script."
    echo 
    echo "Typically, you only need to install the Proxy on one machine to support an entire cluster"
    echo "of machines. If you know the address of an existing proxy and would only want to install"
    echo "and configure collectd on the current machine, you can skip this step."
    echo
    if ask "Do you want to install the Wavefront Proxy?" Y; then
        INSTALL_PROXY="yes"
    fi
    echo
    echo "collectd Installation and Configuration"
    echo "======================================================================================="
    echo
    echo "collectd is a daemon which collects system performance statistics periodically and can be"
    echo "configured to send the collected data to Wavefront. collectd is an open source project with"
    echo "support for many plugins https://collectd.org/wiki/index.php/Table_of_Plugins"
    echo
    echo "If not already installed, this script will attempt to install collectd for your architecture."
    echo "Otherwise, the script will attempt to configure collectd to send data to Wavefront."
    echo
    if ask "Do you want to install and configure collectd?" Y; then
        INSTALL_COLLECTD="yes"
    fi
    echo_title "Starting installation"
else
      echo_title "Beginning automated installation"
fi

echo_step "Preparing to Install"; echo

case $OPERATING_SYSTEM in
    DEBIAN)		
        #
        # Check installation tools.
        #
        echo_step "  Checking installation tools"
        command_exists apt-get || exit_with_failure "Command 'apt-get' not found"
        command_exists tar || exit_with_failure "Command 'tar' not found"
        echo_success
        if command_exists wget; then
            FETCHER="wget --quiet"
        elif command_exists curl; then
            FETCHER="curl --silent"
        else
            exit_with_failure "Either 'wget' or 'curl' are needed"
        fi
        #
        # Check Debian flavor.
        #
        echo_step "  Detecting Debian flavor"
        if command_exists lsb_release; then
            echo -e "\nlsb_release -s -c" >>${INSTALL_LOG}
            CODENAME=$(lsb_release -s -c)
        fi
        if [ -z "$CODENAME" -a -f /etc/lsb-release ]; then
            echo -e "\ngrep '^DISTRIB_CODENAME=' /etc/lsb-release | cut -f2 -d=" >>${INSTALL_LOG}
            CODENAME=$(grep "^DISTRIB_CODENAME=" /etc/lsb-release | cut -f2 -d=)
        fi
        if [ -z "$CODENAME" -a -f /etc/debian_version ]; then
            echo -e "\ncut -d. -f1 /etc/debian_version" >>${INSTALL_LOG}
            CODENAME=$(cut -d. -f1 /etc/debian_version)
        fi
        case "$CODENAME" in
            precise|trusty|xenial)
                FLAVOR="Ubuntu"
                ;;
            wheezy|jessie|stretch|buster|7|8|9|10)
                FLAVOR="Debian"
                ;;
            "")
                exit_with_failure "Unable to detect Debian flavor"
                ;;
            *)
                exit_with_failure "Unsupported Debian flavor: $CODENAME"
                ;;
        esac
        export FLAVOR
        export CODENAME
        echo_step_info "$FLAVOR/$CODENAME"
        check_if_supported && echo_success
        ;;
    REDHAT)
        #
        # Check installation tools.
        #
        echo_step "  Checking installation tools"
        command_exists yum || exit_with_failure "Command 'yum' not found"
        [ -x /sbin/chkconfig ] || exit_with_failure "Command 'chkconfig' not found"
        [ -x /sbin/service ] || exit_with_failure "Command 'service' not found"
        PATH=$PATH:/sbin
        command_exists tar || exit_with_failure "Command 'tar' not found"
        if command_exists wget; then
            FETCHER="wget --quiet"
        elif command_exists curl; then
            FETCHER="curl --silent"
        else
            exit_with_failure "Either 'wget' or 'curl' are needed"
        fi
        echo_success
        #
        # Check RedHat flavor.
        #
        echo_step "  Detecting RedHat flavor"
        if cat /etc/redhat-release 2>/dev/null | grep -q "^CentOS release "; then
            FLAVOR="CentOS"
            echo -e "\ncat /etc/redhat-release 2>/dev/null | cut -f3 -d' ' | cut -f1 -d." >> ${INSTALL_LOG}
            CODENAME=$(cat /etc/redhat-release 2>/dev/null | cut -f3 -d' ' | cut -f1 -d.)
        elif cat /etc/redhat-release 2>/dev/null | grep -q "^CentOS Linux release "; then
            FLAVOR="CentOS"
            echo -e "\ncat /etc/redhat-release 2>/dev/null | cut -f4 -d' ' | cut -f1 -d." >> ${INSTALL_LOG}
            CODENAME=$(cat /etc/redhat-release 2>/dev/null | cut -f4 -d' ' | cut -f1 -d.)
        elif cat /etc/redhat-release 2>/dev/null | grep -q "^Red Hat Enterprise Linux Server release "; then
            FLAVOR="RHEL"
            echo -e "\ncat /etc/redhat-release 2>/dev/null | cut -f7 -d' ' | cut -f1 -d." >> ${INSTALL_LOG}
            CODENAME=$(cat /etc/redhat-release 2>/dev/null | cut -f7 -d' ' | cut -f1 -d.)
        elif cat /etc/system-release 2>/dev/null | grep -q "^Amazon Linux AMI release "; then
            FLAVOR="AMAZON"
            echo -e "\ncat /etc/system-release 2>/dev/null | cut -f5 -d' '" >> ${INSTALL_LOG}
            CODENAME=$(cat /etc/system-release 2>/dev/null | cut -f5 -d' ')
        else
            exit_with_failure "Unable to detect RedHat flavor"
        fi
        export FLAVOR
        export CODENAME
        echo_step_info "$FLAVOR/$CODENAME"
        check_if_supported && echo_success
        ;;
esac

if [ -n "$INSTALL_PROXY" ]; then
    if [[ "$FLAVOR/$CODENAME" == "RHEL/5" ]]; then
        exit_with_failure "Wavefront proxy not yet supported for RHEL/5"
    fi
    if [ -z "$SERVER" ]; then
        get_input "Please enter the Wavefront URL:" "https://try.wavefront.com/api/"
        SERVER=$user_input
    fi
    # Remove the trailing slash if it exists.
    SERVER=${SERVER%/}

    if [[ ! "$SERVER" =~ ^https ]] && [[ -z "$ALLOW_HTTP" ]]; then
        exit_with_failure "Refusing to connect to $SERVER since it is not https."
    fi

    if [ -z "$TOKEN" ]; then
        get_input "Please enter your Wavefront token:" ""
        TOKEN=$user_input
    fi
    echo_step "  Testing token against $SERVER/daemon/test?token=$TOKEN"
    if command_exists curl; then
        STATUS=$(curl -sL -w "%{http_code}" -X POST $SERVER/daemon/test?token=$TOKEN -o /dev/null)
    elif command_exists wget; then
        STATUS=$(wget --method=POST -O /dev/null $SERVER/daemon/test?token=$TOKEN 2>&1 | grep -F HTTP | cut -d ' ' -f 6)
    fi

    case $STATUS in
    200)
        echo_success
        ;;
    401)
        exit_with_failure "Failed to validate token. Token ($TOKEN) does not belongs to a user with Agent Management permissions. ($STATUS)"
        ;;
    404)
        echo_warning "Failed to validate token. ($STATUS) Will attempt to proceed."
        ;;
    *)
        exit_with_failure "Failed to validate token. Please confirm that the URL is valid ($SERVER) and that the token ($TOKEN) belongs to a user with Agent Management permissions. ($STATUS)"
        ;;
    esac

    case $OPERATING_SYSTEM in
    DEBIAN)		
        echo_step "Installing Wavefront Proxy (Debian) with token: $TOKEN for cluster at: $SERVER"; echo		
        echo_step "  Setting up Repo"
        curl -s $PACKAGE_CLOUD_DEB | bash >>${INSTALL_LOG} 2>&1
        if [ $? -ne 0 ]; then
          exit_with_failure "Failed to configure APT repository for Wavefront Proxy"
        fi
        echo_success
        echo_step "  Installing via apt-get"
        apt-get -qq -y install wavefront-proxy >>${INSTALL_LOG} 2>&1
        if [ $? -ne 0 ]; then
            exit_with_failure "Failed to install the Wavefront Proxy with APT"
        fi
        echo_success
        ;;
    REDHAT)
        echo_step "Installing Wavefront Proxy (RedHat) with token: $TOKEN for cluster at: $SERVER"; echo
        echo_step "  Setting up Repo"
        curl -s $PACKAGE_CLOUD_RPM | bash >>${INSTALL_LOG} 2>&1
        if [ $? -ne 0 ]; then
            exit_with_failure "Failed to configure YUM repository for Wavefront Proxy"
        fi
        echo_success
        echo_step "  Installing via yum"
        echo -e "\nyum -y -q clean metadata" >>${INSTALL_LOG}
        yum -y -q clean metadata >>${INSTALL_LOG} 2>&1
        echo -e "\nyum -y -q install wavefront-proxy" >>${INSTALL_LOG}
        yum -y -q install wavefront-proxy >>${INSTALL_LOG} 2>&1
        if [ $? -ne 0 ]; then
            exit_with_failure "Failed to install the Wavefront Proxy with Yum"
        fi
        echo_success
        ;;
    esac

    echo_step "  Modifying Configuration File at $CONF_FILE"
    # Update the configuration file
    if [ -f $CONF_FILE ]; then
        if grep -q ^#server $CONF_FILE; then
            sed -ri s,^#server.*,server=$SERVER,g $CONF_FILE
        else
            sed -ri s,^server.*,server=$SERVER,g $CONF_FILE
        fi
        if grep -q ^#token $CONF_FILE; then
            sed -ri s,^#token.*,token=$TOKEN,g $CONF_FILE
        else
            sed -ri s,^token.*,token=$TOKEN,g $CONF_FILE
        fi
    else
        exit_with_failure "Failed to locate $CONF_FILE"
    fi

    echo_success
    # Start the service.
    echo_step "  Starting Service"
    service wavefront-proxy restart >>${INSTALL_LOG} 2>&1
    if [ $? -ne 0 ]; then
        exit_with_failure "Failed to start the Wavefront Proxy"
    fi
    echo_success
fi

if [ -n "$INSTALL_COLLECTD" ]; then
    if [ -z "$PROXY" ]; then
        get_input "Please enter the Wavefront Proxy Address:" "localhost"
        PROXY=$user_input
    fi
    if [ -z "$PROXY_PORT" ]; then
        get_input "Please enter the Wavefront Proxy Port:" "4242"
        PROXY_PORT=$user_input
    fi

    case $OPERATING_SYSTEM in
    DEBIAN)
        echo_step "Installing CollectD (Debian)"; echo
        echo_step "  Installing software-properties-common"
        apt-get install software-properties-common -qq >>${INSTALL_LOG} 2>&1
        if [ $? -ne 0 ]; then
            exit_with_message "Failed to install software-properties-common"
        fi
        echo_success
        echo_step "  Adding collectd 5.5 ppa repository"
        add-apt-repository ppa:collectd/collectd-5.5 -y >>${INSTALL_LOG} 2>&1
        if [ $? -ne 0 ]; then
            exit_with_message "Failed to add collectd repo ppa:collectd/collectd-5.5 to APT"
        fi
        echo_success
        echo_step "  Installing collectd via apt-get"
        apt-get update >>${INSTALL_LOG} 2>&1
        if [ $? -ne 0 ]; then
            echo_warning "Failed to do apt-get update, will attempt to continue"
        fi
        apt-get -qq -y install collectd -qq >>${INSTALL_LOG} 2>&1
        if [ $? -ne 0 ]; then
            exit_with_message "Failed to do install collectd with APT"
        fi
        echo_success
        ;;
    REDHAT)
        if command_exists wget; then
            FETCHER="wget --quiet"
        elif command_exists curl; then
            FETCHER="curl --silent -o $REDHAT_PUBLIC_KEY_FILE"
        else
            exit_with_failure "Either 'wget' or 'curl' are needed"
        fi
        echo_step "Installing CollectD (RedHat)"; echo
        #
        # Add yum source.
        #	
        echo_step "  Adding repository"
        if [ -d /etc/yum.repos.d ]; then
            cat > /etc/yum.repos.d/collectd-ci.repo <<EOF
[collectd-ci]
name=collectd CI
baseurl=http://pkg.ci.collectd.org/rpm/collectd-5.5/epel-$CODENAME-$ARCHITECTURE
enabled=1
gpgkey=http://pkg.ci.collectd.org/pubkey.asc
gpgcheck=1
repo_gpgcheck=1
priority=9
EOF
        if [[ "$CODENAME" == "5" ]]; then
            # Collectd package for RHEL5 does not support GPG signing.
            sed -ri '/gpg/d' /etc/yum.repos.d/collectd-ci.repo
            echo "gpgcheck=0" >> /etc/yum.repos.d/collectd-ci.repo
        fi
        else
            exit_with_failure "Package resource directory not found"
        fi
        echo_success
        echo_step "  Downloading the collectd-ci repo public key"
        echo -e "\n$FETCHER ${REDHAT_REPOSITORY}/${REDHAT_PUBLIC_KEY_FILE}" >>${INSTALL_LOG}
            $FETCHER ${REDHAT_REPOSITORY}/${REDHAT_PUBLIC_KEY_FILE} >>${INSTALL_LOG} 2>&1
        if [ -s "$REDHAT_PUBLIC_KEY_FILE" ]; then
            mkdir -p /etc/pki/rpm-gpg
            mv ${REDHAT_PUBLIC_KEY_FILE} /etc/pki/rpm-gpg/
            echo -e "\nrpm --import /etc/pki/rpm-gpg/${REDHAT_PUBLIC_KEY_FILE}" >>${INSTALL_LOG}
            rpm --import /etc/pki/rpm-gpg/${REDHAT_PUBLIC_KEY_FILE} >>${INSTALL_LOG} 2>&1
            echo_success
        else
            exit_with_failure "Failed downloading the collectd-ci repo public key"
        fi
        echo_step "  Generating yum cache for collectd"
        echo -e "\nyum -q makecache -y --disablerepo='*' --enablerepo='collectd-ci'" >>${INSTALL_LOG}
        yum makecache -y --disablerepo='*' --enablerepo='collectd-ci' >>${INSTALL_LOG} 2>&1
        echo_success
        echo_step "  Cleaning yum metadata"
        echo -e "\nyum -y -q clean metadata" >>${INSTALL_LOG}
        yum -y clean metadata >>${INSTALL_LOG} 2>&1
        echo_success
        echo_step "  Installing collectd"
        echo -e "\nyum -y -q install collectd" >>${INSTALL_LOG}
        yum -y install collectd >>${INSTALL_LOG} 2>&1
        if [ "$?" != 0 ]; then
            exit_with_failure "Failed to install collectd"
        fi

        # new plugins installation
        yum_quiet_install COLLECTD_PLUGINS
        echo_success
        ;;
    esac

    if [ -z "$OVERWRITE_COLLECTD_CONFIG" ]; then
        echo
        echo "We recommend using Wavefront's collectd configuration for initial setup"
        if ask "Would you like to overwrite any existing collectd configuration? " N; then
            OVERWRITE_COLLECTD_CONFIG="yes"
            APP_CONFIGURE="yes"
        else
            APP_CONFIGURE="no"
            APP_FINISHED="yes"
            echo
            echo "The write_tsdb plugin is required to send metrics from collectd to the Wavefront Proxy"
            echo "Manual setup is required"
            echo
        fi
    fi

    if [ -n "$OVERWRITE_COLLECTD_CONFIG" ]; then
        if command_exists wget; then
            FETCHER="wget --quiet -O /tmp/collectd_conf.tar.gz"
        elif command_exists curl; then
            FETCHER="curl -L --silent -o /tmp/collectd_conf.tar.gz"
        else
            exit_with_failure "Either 'wget' or 'curl' are needed"
        fi
        echo_step "  Configuring collectd"
        $FETCHER https://github.com/kentwang929/install/files/394998/default_collectd_conf.tar.gz >>${INSTALL_LOG} 2>&1
        echo_success
        echo_step "  Extracting Configuration Files"
        if [ ! -d "/etc/collectd" ]; then
            mkdir -p /etc/collectd
        fi
        tar -xf /tmp/collectd_conf.tar.gz -C /etc/collectd >>${INSTALL_LOG} 2>&1
            if [ "$?" != 0 ]; then
                exit_with_failure "Failed to extract configuration files"
            fi
        echo_success

        case $OPERATING_SYSTEM in
        REDHAT)
            echo_step "  Overwriting collectd.conf"	
            mv /etc/collectd.conf /etc/collectd.conf.bak
            mv /etc/collectd/collectd.conf /etc/collectd.conf
            echo_success
            ;;
        esac
        
        echo_step "  Modifying Configuration File at $COLLECTD_WAVEFRONT_CONF_FILE"
        # Update the configuration file
        sed -ri s,Host\\s+.*$,"Host \"$PROXY\"",g $COLLECTD_WAVEFRONT_CONF_FILE
        sed -ri s,Port\\s+.*$,"Port \"$PROXY_PORT\"",g $COLLECTD_WAVEFRONT_CONF_FILE
        echo_success
        echo_step "  Restarting collectd"
        service collectd restart >>${INSTALL_LOG} 2>&1
        echo_success
    fi

    if [ -z "$APP_CONFIGURE" ]; then
        echo
        if ask "Would you like to configure collectd based on your installed app? " Y; then
            APP_CONFIGURE="yes"
        else
            echo
            echo "Keeping the default configuration"
            echo
            APP_CONFIGURE="no"
            APP_FINISHED="yes"
        fi
    fi

    if [ "$APP_CONFIGURE" == "yes" ]; then
        if command_exists wget; then
            FETCHER="wget --quiet -O /tmp/WF-CDPInstaller.tar.gz"
        elif command_exists curl; then
            FETCHER="curl -L --silent -o /tmp/WF-CDPInstaller.tar.gz"
        else
            exit_with_failure "Either 'wget' or 'curl' are needed"
        fi
        echo_step "  Pulling application configuration file"
        APP_LOCATION="https://github.com/kentwang929/install/files/400050/WF-CDPInstaller.tar.gz"
        $FETCHER $APP_LOCATION >>${INSTALL_LOG} 2>&1
        echo_success
        echo_step "  Extracting Configuration Files"
        if [ ! -d "/tmp/WF-CDPInstaller" ]; then
            mkdir -p /tmp/WF-CDPInstaller
        fi
        tar -xf /tmp/WF-CDPInstaller.tar.gz -C /tmp/WF-CDPInstaller >>${INSTALL_LOG} 2>&1
        if [ "$?" != 0 ]; then
            exit_with_failure "Failed to extract configuration files"
        fi
        echo_success
        if command_exists python; then
            cd /tmp/WF-CDPInstaller/$APP_CONFIGURE_NAME
            python -m python_installer.gather_metrics ${OPERATING_SYSTEM} ${INSTALL_LOG}
            if [ "$?" == 0 ]; then
                APP_FINISHED="yes"
            fi
        else
            echo_warning "Python is needed to enable the app configure installation"
        fi
    fi

fi

if [ "$APP_FINISHED" == "yes" ]; then
    echo_step "  Restarting collectd"
    service collectd restart >>${INSTALL_LOG} 2>&1
    echo_success
    echo
    echo "======================================================================================="
    echo "SUCCESS"
fi


if [ -n "$INSTALL_PROXY" ]; then
    echo
    echo "The Wavefront Proxy has been successfully installed. To test sending a metric, open telnet to the port 2878 and type my.test.metric 10 into the terminal and hit enter. The metric should appear on Wavefront shortly. Additional configuration can be found at $CONF_FILE. A service restart is needed for configuration changes to take effect."
fi

if [ -n "$INSTALL_COLLECTD" ] && [ "$APP_FINISHED" == "yes" ] && [ -n "$OVERWRITE_COLLECTD_CONFIG" ]; then
    echo
    echo "CollectD has been successfully installed and configured. Additional configurations can be found at /etc/collectd/managed_config/. Check /var/log/collectd.log for errors regarding writing metrics to the Wavefront Proxy by grepping for write_tsdb"
fi

if [ "$APP_CONFIGURE" == "yes" ]; then
    echo "To restart WF-CDPInstaller"
    echo "Navigate to /tmp/WF-CDPInstaller/$APP_CONFIGURE_NAME and type"
    echo "python -m python_installer.gather_metrics"
    echo "Restart the collectd service afterward to see the change"
fi
