# pysshtun
A simplistic daemon to tunnel a set of local ports to a set of remote ports over SSH. Keeps iptables up-to-date for transparent integration.

# Platforms
Somehow is not capable of detecting killed processes on OS X.

# Running
```
# Start pysshtun
> python -m pysshtun -P google.mainserver:www.google.com:127.0.0.2:9999:127.0.0.1:5432
# The next request is going to be re-routed through our local tunnel at 127.0.0.2:9999 to 127.0.0.1:5432 using ssh host defined by alias google.mainserver
> nc www.google.com 5432
```
