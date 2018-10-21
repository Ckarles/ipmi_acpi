IPMI_ACPI
=========
Automation tool to send acpi commands to asrock-rack's ipmi web interface.

Usage
-----
::

  $ ipmi_acpi --help
  Usage: ipmi_acpi [OPTIONS] HOST

    sends acpi commands to an asrock ipmi host

  Options:
    -u, --username TEXT
    -p, --password TEXT
    -c, --command [status|start|stop|force-stop|reset]
                                    command to send to ipmi interface  [default: status; required]
    --help                          Show this message and exit.

example:
::

  $ ipmi_acpi -u admin websrv02_ipmi.local -c start
  Password:
  Command: start
  Connecting to: websrv02_ipmi.local...
  Connected!
  Ipmi status: Host is currently off
  Performing Power Action..Please Wait
  Ipmi status: Host is currently on


Dependencies
------------

- selenium
- chromium with headless support (chrome 60+)
- chromedriver_

.. _chromedriver: https://github.com/SeleniumHQ/selenium/wiki/ChromeDriver


Important note
--------------

It is unknown why, but this doesn't work with self-generated CA's SSL certificate,
so the username / password are sent in plain text using unencrypted http!

Please to keep that in mind and only use this script in a trusted network or through an encrypted tunnel.
