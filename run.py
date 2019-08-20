import os, pickle, sys, requests, time, datetime
from os import scandir
import paho.mqtt.client as mqtt_

# SETTINGS
working_directory = "/opt/scripts/notify" #directory where this file is stored
monitored_path = "/var/lib/motioneye/Camera1" #path that is monitored, including all subfolders
monitored_fileendings = ["jpg", "JPG", "JPEG", "jpeg"]  #fileendings that should be notified

pushover_token = "your token" #your pushover Application token
pushover_user = "your user" #your pushover user id

notification_title = "MOTION DETECTED"  #title for the notification
notification_message = "Detected Motion!" #message for the notification

mqtt_ip = "your ip" #your mqtt server
mqtt_topic = "your topic" #if you push a 'ON' in this topic notifications get enabled, everything else will disable them

cycle_time = 5  #time in seconds until the folder gets scanned again

#Set working directory
os.chdir(working_directory)

class DirMonitoring():
    def __init__(self, monitored_path, fileendings, pushover_token, pushover_user, notification_message, notification_title, status):
        self.fileendings = fileendings
        self.token = pushover_token
        self.user = pushover_user
        self.message = notification_message
        self.title = notification_title
        self.status = status
        self.monitored_path = monitored_path
        self.last_notify = datetime.datetime.now() - datetime.timedelta(days=1)

    def start(self):
        self.filelist = self.loadObj()
        self.scan(self.monitored_path)
        self.saveObj()

    # load filelist
    def loadObj(self):
        if not os.path.exists("obj"):
            os.makedirs("obj")

        try:
            with open('obj/' + "filelist" + '.pkl', 'rb') as f:
                return pickle.load(f)
        except:
            print("Filelist not found, create a new one")
            return []

    def saveObj(self):
        with open('obj/'+ "filelist" + '.pkl', 'wb') as f:
            pickle.dump(self.filelist, f, pickle.HIGHEST_PROTOCOL)

    def scan(self, path):
        print("Scan directory")
        for entry in scandir(path):
            if entry.is_dir(follow_symlinks=False):
                self.scan(entry.path)
            else:
                cnt = 0
                for file in self.filelist:
                    if str(entry.path) == str(file):
                        cnt = 1
                if cnt == 0:
                    print((datetime.datetime.now()-self.last_notify)/datetime.timedelta(minutes=1))
                    print(self.status)
                    #check if it should notify,the > 5 does stop notification for 5 minutes after each notification, change that if you want
                    if self.status == True and (datetime.datetime.now()-self.last_notify)/datetime.timedelta(minutes=1) > 5 and entry.path.rsplit('.', 1)[1] in self.fileendings:
                        self.notify(str(entry.path))
                        self.last_notify = datetime.datetime.now()
                    else:
                        print("New File detected, but silence mode is enabled")
                    self.filelist.append(str(entry.path))
                #print(str(entry.path))

    def notify(self, path):
        payload={'token': self.token, 'user': self.user, 'message': self.message, 'html': 1, 'title': self.title, 'priority': 1}
        #print (path.rsplit('.', 1)[1])
        if path.rsplit('.', 1)[1] in self.fileendings:
            print("Send Notification...")
            if path.rsplit('.', 1)[1] in ['JPG', 'jpg', 'jpeg', 'jpg']:
                response = requests.post("https://api.pushover.net/1/messages.json", data=payload, files={"attachment": ("image.jpg", open(path, "rb"), "image/jpeg")})
                print(response)
            else:
                response = requests.post("https://api.pushover.net/1/messages.json", data=payload)
                print(response)
    def updateStatus(self, status):
        self.status = status


class mqtt():
    def __init__(self, server, channel):
        self.client = mqtt_.Client()
        self.client.on_connect=self.onconnect
        self.client.on_message=self.onmessage
        self.client.connect(server)
        self.channel = channel
        self.status = False
        self.client.subscribe(self.channel)
        self.client.loop_start()

    def onconnect(self, client, userdata, flags, rc):
        print("Connected to MQTT")

    def onmessage(self, client, userdata, msg):
        if str(msg.payload, 'utf-8') == 'ON':
            self.status = True
            print("Changed status to ON")
        else:
            self.status = False
            print("Changed status to OFF")

    def getStatus(self):
        return self.status

#if you do not want to use mqtt make sure that mqtt.getStatus() in the next lines is replaced with something that returns True (notifcations enabled) or False (notifications disabled)
mqtt = mqtt(mqtt_ip, mqtt_channel)


run = DirMonitoring(monitored_path, monitored_fileendings, pushover_token, pushover_user, notification_message, notification_title, mqtt.getStatus())
while True:
    run.updateStatus(mqtt.getStatus())
    run.start()
    time.sleep(cycle_time)
