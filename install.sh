#!/bin/bash
# Install Wavefront Proxy and configures standard collectd plugin
# ####

function logo {
cat <<"EOT"
 __      __                     _____                      __   
/  \    /  \_____ ___  __ _____/ ____\______  ____   _____/  |_ 
\   \/\/   /\__  \\  \/ // __ \   __\\_  __ \/  _ \ /    \   __\
 \        /  / __ \\   /\  ___/|  |   |  | \(  <_> )   |  \  |  
  \__/\  /  (____  /\_/  \___  >__|   |__|   \____/|___|  /__|  
       \/        \/          \/                         \/      
EOT
}

function usage {
	echo
	echo "USAGE"
	echo "====="
	echo "$0 [ --proxy | --collectd | --server <server_url> | --token <token> | --proxy <proxy_address> | --proxy_port <port>"
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
	echo "    --proxy <proxy_address>"
	echo "          The address of the proxy to send data to. Defaults to localhost."
	echo "    --proxy_port <port>"
	echo "          The proxy port to send collectd data to. Defaults to 4242."
	echo
}

echo
echo
logo
echo
echo
echo "Wavefront Proxy / CollectD Installation Script"
echo "=============================================="
echo

# Input arguments
INSTALL_PROXY=""
INSTALL_COLLECTD=""
SERVER=""
TOKEN=""
PROXY="localhost"
PROXY_PORT="4242"

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
		--server)
			SERVER=$2
			shift 2
			;;
		--token)
			TOKEN=$2
			shift 2
			;;
		--proxy)
			PROXY=$2
			shift 2
			;;
		--proxy_port)
			PROXY_PORT=$2
			shift 2
			;;
		*)
			if [ -z "$1" ]; then
				break
			else
				usage
				exit 1
			fi
			;;
	esac
done


if [ -n "$INSTALL_PROXY" ]; then
	if [ -z "$SERVER" ]; then
		echo "Must specify --server to install proxy"
		usage
		exit 1
	fi
	if [ -z "$TOKEN" ]; then
		echo "Must specify --token to install proxy"
		usage
		exit 1
	fi
	echo "Installing Wavefront Proxy with token: $TOKEN for cluster at: $SERVER"
fi

if [ -n "$INSTALL_COLLECTD" ]; then
	if [ -z "$PROXY" ]; then
		echo "Must specify --proxy to install and configure collectd"
		usage
		exit 1
	fi
	if [ -z "$PROXY_PORT" ]; then
		echo "Must specify --proxy_port to install and configure collectd"
		usage
		exit 1
	fi
	echo "Installing CollectD"
fi
