

import sys
import time
import datetime
import json
import urllib2
import requests
import calendar

argCluster = sys.argv[1]
argToken = sys.argv[2]
argSource = sys.argv[3]
argMetric = sys.argv[4]

wfhost = argCluster  # example : 'https://metrics.wavefront.com'

wfauth = argToken
source = argSource

q = 'ts("'+argMetric+'", source='+source+')'

#query from one minute ago
epoch_time = calendar.timegm(time.gmtime()) - 60
s = str(epoch_time) + "000"

url = wfhost + "/chart/api?q=" + q + "&s=" + s + "&strict=true"
headers = {'X-AUTH-TOKEN': wfauth}

r = requests.get(url, headers=headers)

success = False
numSeries = 0
numPoints = 0

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
