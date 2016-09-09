#!/bin/bash
# ./test.sh url keyword
# input:
#     url - where the one line installer script resides
#     keymetric - metric name to search
# output:
#     exit code from executing plugin_tester.py


function usage() {
    echo
    echo "USAGE"
    echo "====="
    echo "test.sh [ --src_url <one line installer script url> | --keymetric <keywords> ]"
    echo
    echo "    --src_url <url>"
    echo "          The token to register the agent. Must have agent management permissions"
    echo
    echo "    --keymetric <keyword>"
    echo "          metric name to intercept from collecting agents"
    echo
    echo "    --help"
    echo "          print out the usage"
    echo
}


# Input arguments
SRC_URL=""
KEYMETRIC=""


while :
do
    case $1 in
        --help)
            usage
            exit 0
            ;;
        --src_url)
            SRC_URL=$2
            shift 2
            ;;
        --keymetric)
            KEYMETRIC=$2
            shift 2
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
      
if [ -z "$SRC_URL" ] || [ -z "$KEYMETRIC" ]; then
    echo "Both args have to be supplied!"
    usage
    exit 1
fi

# one line installer
bash -c "$(curl -sL ${SRC_URL})" "--" "--test_app_configure"
python plugin_tester.py "${KEYMETRIC}"

# if plugin_tester return failure code,
# grab the log from collectd to output failure
if [ $? -ne 0 ]; then
    if [ -e "/var/log/collectd.log" ]; then
        cat /var/log/collectd.log
    else
        echo -e "\nTest has failed, but no log message can be found."
    fi
    exit 1
fi
