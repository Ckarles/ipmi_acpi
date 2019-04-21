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
    -b, --browser [firefox|chrome]  [default: firefox; required]
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
- recent Chromium OR firefox along its respective driver
+ geckodriver_ (for Firefox)
+ chromedriver_ (for Chromium / Google Chrome)

.. _geckodriver: https://github.com/mozilla/geckodriver/releases
.. _chromedriver: https://github.com/SeleniumHQ/selenium/wiki/ChromeDriver
