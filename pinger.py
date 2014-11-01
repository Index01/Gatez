#!/usr/bin/env python2
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

SCHEMA_VERSION = 1

import time
import subprocess
from datetime import datetime
from mongoengine import *


hosts = { "internet" : [ "4.2.2.2" ], "vendor" : ["www.ticketfly.com"] }
interval = 10 # seconds


print "Starting Pinger..."

try:
    connect("gayte")
except Exception, e:
    print "Could not connect to local mongodb server", e
    time.sleep(10)
    exit(1)

print "MongoDB connection established..."

class LatencyReport(Document):
    schema_version = IntField(default=SCHEMA_VERSION)
    timestamp = DateTimeField(default=datetime.now)
    category = StringField(required=True)
    target = StringField(required=True)
    latency = FloatField()

    meta = { 
            'index_backround': True,
            'indexes' : [ 'timestamp', 'category', 'target']
             } 


def handlefail(category, target):
    try:
        report = LatencyReport(category=category, target=target, latency = -1)
        report.save()
    except Exception, e: 
        print "handleFail", e
        sleep(5)

def handlesuccess(category, target, rtt):
    try:
        report = LatencyReport(category=category, target=target, latency = rtt)
        report.save()
    except Exception,  e:
        print "handleSuccess", e
        time.sleep(5)


def doping(target): 
     child = subprocess.Popen(["ping", "-c", "1", target], stdout=subprocess.PIPE)
     streamdata = child.communicate()[0]
     rc = child.returncode
     return rc, streamdata 

while True:
    for category in hosts:
        for target in hosts[category]:
            exit, out = doping(target)
            if exit == 0:
                rtt = float(out.split(" = ")[1].split("/")[0])
                handlesuccess(category, target, rtt)
            else:
                handlefail(category, target)
    time.sleep(interval)
