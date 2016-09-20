

import sys
import time
import datetime
import json
import urllib2
import requests
import socket
import calendar
from pprint import pprint
# json.load(urllib2.urlopen(""))

#https://metrics.wavefront.com/chart/api?q=ts("cpu.loadavg.1m", source="cluster*")&s=1437838200000&e=1438433400000&strict=true&includeObsoleteMetrics=true

argCluster = sys.argv[1]
argToken = sys.argv[2]
argSource = sys.argv[3]
argMetric = sys.argv[4]

# Configure HOST Url: host
wfhost = 'https://'+argCluster+'.wavefront.com'  # example : 'https://metrics.wavefront.com'

# Configure API key authorization: api_key
wfauth = argToken
# Uncomment below to setup prefix (e.g. BEARER) for API key, if needed
# wavefront_client.configuration.api_key_prefix['X-AUTH-TOKEN'] = 'BEARER'
source = argSource

q = 'ts("'+argMetric+'", source='+source+')'

#query from one minute ago
epoch_time = calendar.timegm(time.gmtime()) - 60
s = str(epoch_time) + "000"

#print s

url = wfhost + "/chart/api?q=" + q + "&s=" + s + "&strict=true"
headers = {'X-AUTH-TOKEN': wfauth}

r = requests.get(url, headers=headers)

success = False
numSeries = 0
numPoints = 0

#print r.status_code

if r.status_code == 200:
    data = r.json()
    data = data['timeseries']
    #print data
    numSeries = len(data)
    for series in data:
        if len(series['data']) > 0:
            numPoints += len(series['data'])
            success = True

if success:
    print ("%s - SUCCESS - %s returned %d series and %d points.") % (datetime.datetime.now(), source, numSeries, numPoints)
else:
    print ("%s - FAILURE - %s returned 0 points.") % (datetime.datetime.now(), source)
