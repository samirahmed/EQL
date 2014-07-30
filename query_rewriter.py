import os, json, sys
from datetime import datetime
import requests as api

datetime_server = "http://mangosteen-datetime.azurewebsites.net"

def augment_datetime(raw):
  resp = api.get(datetime_server, params = {"date": raw})
  if (resp.status_code == 200):
    if (resp.text != "null"):
      date =  datetime.strptime(str(resp.text), "%d-%b-%Y")
      return date.strftime('%Y-%m-%dT%H:%M:%S-07:00')
  else:
    return datetime

def augment(query):
  if query.date:
    print "augmenting"
    augmented = augment_datetime(query.date)
    if augmented:
      query.date_is_parsed = True
      query.date = augmented

