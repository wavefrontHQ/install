# Wavefront Agent and Collectd Installer

The Wavefront Agent and Collectd Installer is a single script that can quickly install the tools needed to send your metrics to Wavefront.

The script can be run in interactive mode, or in automatic mode by passing command line arguments.

## Interactive Mode
```
sudo bash -c "$(curl -sL https://raw.githubusercontent.com/kentwang929/install/my_branch/install.sh)"
```
When running the script above as is, without any further command line arguments, the installer will prompt you for the following:

- **proxy [y/n]** -
    Answer yes to initiate agent installation.   
- **server [server_url]** -
    The URL of the Wavefront cluster that data should be sent to.
- **token [token]** - 
    The token to register the agent. Tokens can be generated/retrieved from your Wavefront profile page
- **collectd [y/n]** -
    Answer yes to initiate collectd installation.
- **proxy_address [proxy_address]** - 
    The address where the Wavefront proxy is installed. This is usually "localhost" if you're installing on the same machine.
- **proxy_port [port]** - 
    The port that the agent should be listening on.
- **overwrite_collectd_config [y/n]** - 
    Answering yes will configure collectd to send metrics to the wavefront agent.
- **app_configure [y/n]** -
    Answering yes will run the mini installer that detects and configure the appropriate collectd configuration files.  Answering no will keep the default configuration file.  This command has to be entered along with overwrite_collectd_config argument.

## Non-interactive Mode

The script is also useful for automatically deploying the Wavefront Proxy or Collectd accross multiple servers.

For example, to install the Wavefront Agent without prompting the user for input during the install:
```
sudo bash -c "$(curl -sL https://goo.gl/c70QCx)" -- --proxy --server https://COMPANY_NAME.wavefront.com/api/ --token YOUR_API_TOKEN
```
For Collectd:
```
sudo bash -c "$(curl -sL https://goo.gl/c70QCx)" -- --collectd --proxy_address localhost --proxy_port 4242 --overwrite_collectd_config
```
