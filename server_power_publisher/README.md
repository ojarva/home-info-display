Server power
============

Configuration:

Put your server's configuration to local_settings.py:
```
SERVER_MAC_ADDRESS="21:32:6b:2b:23:b9"
SERVER_IP_ADDRESS="192.168.1.120"
SERVER_SSH_USERNAME="powercontrol"
SERVER_BROADCAST_IP="192.168.1.255"
```

Execute run.py with supervisord or similar daemon.
