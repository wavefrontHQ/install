# Wavefront PCInstaller Integration Test

## Files to consider:
+ integration\_test.sh
+ docker\_dir/test\_scripts/test.sh
+ docker\_dir/test\_script/plugin\_tester.py
+ docker\_dir/helpers contain helpful files
+ that Dockerfiles may need when setting up the environment
+ \*Dock are Dockerfiles

## Main usage:
run ./integration\_test to begin testing
    
    Note:
        Change the one line installer src link with the var SRC\_URL
        to test different installer.

## Script explaination:
integration\_test.sh
    The script to be called when testing one line installer
    integration.

    description:
        Builds the base docker image.
        For each application that the installer is testing against,
        build the appropriate environment using the
        Dockfile located under /docker\_dir and runs
        the container with by providing the appropriate
        parameters.
    
scripts locate under  /docker\_dir/test\_script
pulled into the testing environment to run
the one line installer and listen for the metrics

test.sh [ --src\_url <url> | --keymetric <keyword> ]
    Script within the docker container that accepts
    one line installer script src url and a keymetric.

    description: 
        Runs the one line installer via sudo bash -c curl.
        call plugin\_tester.py by passing keymetric.

plugin\_tester.py [keymetric]
    Acts as proxy and listen to default opentsdb port (4242)

    description:
        Listen to the socket at 4242 and check whether
        keymetric is reported by collecting agent (TELEGRAF|COLLECTD).
