Ping
====

Configuration:

Install fping.

Put your destinations to local_settings.py:
```
DESTINATIONS=["ping.funet.fi", "www.saunalahti.fi", "www.google.com", "192.168.1.254"]
```

Execute run.py with supervisord or similar daemon.

