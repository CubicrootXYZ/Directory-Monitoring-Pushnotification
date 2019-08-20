# Directory-Monitoring-Pushnotification
Notifies you via Pushover if there is a new file in a directory, controlled via MQTT. Used to alert motion detected by motion eye. If there is a new JPG-file it will be sent with the notification.

## Installation
1. Copy the run.py in a directory of your choice
2. Change the working directory and the monitored directory to your needs (first lines in the run.py)
3. Add the Pushover token and user
4. Make sure you run a MQTT server, add the IP and the channel for enabling/disabling notifications
5. Add a systemd job. Your .service file should look like that. Make sure you add a RestartSec, thats needed because else it will restart to quickly before network connection is available and run into an error
```
[Unit]
Description=DirMonitoring

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/scripts/notify/run.py
Restart=always
RuntimeMaxSec=43200
RestartSec=60

[Install]
WantedBy=multi-user.target

```
6. Enable and start the systemd job with
```
$ systemctl enable jobname.service
$ systemctl start jobname.service
```

## Customization

**Replace MQTT**

You can replace MQTT as enabler/disabler by replacing the mqtt class with any other service you want. Just make sure that there is a mqtt.getStatus() that returns True (enable notifications) or False (disable notifications). You also can just replace the mqtt.getStatus() in the initialization of DirMonitoring-class and when calling DirMonitoring.start() with True to always get notifications. 
