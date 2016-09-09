# Wavefront PCInstaller Integration Test

## Files to consider:
+ integration\_test.sh
+ docker\_dir/test\_scripts/test.sh
+ docker\_dir/test\_script/plugin\_tester.py
+ docker\_dir/helpers contain helpful files
that Dockerfiles may need when setting up the environment
+ \*Dock are Dockerfiles

## Main usage:
####./integration\_test.sh

Run the script to begin testing
    
    Note:
        Change the one line installer src link with the var SRC_URL
        to test different installer.

## Script explaination:
####integration\_test.sh

The script to be called when testing one line installer
integration.

    Description:
        Builds the base docker image.
        For each application that the installer is testing against,
        build the appropriate environment using the
        Dockfile located under /docker_dir and runs
        the container with by providing the appropriate
        parameters.

    Note:
        init.sh files are often invoked in docker run command.
        They are needed because docker 1.12 cannot start the
        service within Dockerfiles.  An external script
        needs to be invoked to start the service after starting
        the container.

    
**Below are scripts locate under  /docker\_dir/test\_script
that are pulled into the testing environment to run**

####test.sh [ --src\_url <url> | --keymetric <keywords> ]

Script within the docker container that accepts
one line installer script src url and keymetrics separated
by space.

    Description: 
        Runs the one line installer via sudo bash -c curl.
        call plugin_tester.py by passing keymetric.

####plugin\_tester.py [keymetrics]

Acts as proxy and listen to default opentsdb port (4242)

    Description:
        Listen to the socket at 4242 and check whether
        keymetrics are reported by the collecting agent (TELEGRAF|COLLECTD).
