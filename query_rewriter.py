import os, json, sys
from datetime import datetime
import requests as api
import es_dictionary as es

datetime_server = es.GetConfig()["dateServiceUrl"]

def augment_datetime(raw):
  resp = api.get(datetime_server, params = {"date": raw})
  if (resp.status_code == 200):
    if (resp.text != "null"):
      date =  datetime.strptime(str(resp.text), "%d-%b-%Y")
      return date.strftime('%Y-%m-%dT%H:%M:%S-07:00')

  else:
    return None

def augment(query):
  if query.date:
    print "augmenting"
    augmented = augment_datetime(query.date)
    if augmented:
      if query.date_comparator == None:
          if "day" in query.date:
            query.scope = "day"

      query.date_is_parsed = True
      query.date = augmented
