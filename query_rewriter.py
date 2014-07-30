import os, json, sys
from datetime import datetime, timedelta, date
import requests as api
import es_dictionary as es

datetime_server = es.GetConfig()["dateServiceUrl"]
months = ["january","february","march","april","may","june","july","august","september","october","november","december","jan","feb","march","april","may","jun","jul","aug","sep","oct","nov","dec"]
days = ["monday","mon","tuesday","tues","wednesday","wed","thursday","thurs","friday","fri","saturday","sat","sunday","sun"]

def augment_datetime(raw):
  resp = api.get(datetime_server, params = {"date": raw})
  if (resp.status_code == 200):
    if (resp.text != "null"):
      return datetime.strptime(str(resp.text), "%d-%b-%Y")
  else:
    return None

def augment(query):
  if query.date:
    print "augmenting"
    if query.date in days:
        query.scope = "day"
    elif query.date in months:
        query.scope = "month"
    date_temp = None
    if query.date == "this year":
        date_temp = date(datetime.now().year,1,1)
    elif query.date == "this month":
        date_temp = date(datetime.now().year, datetime.now().month, 1)
    else:
        date_temp = augment_datetime(query.date)
        if datetime.now().year < date_temp.year:
            date_temp.year = datetime.now().year
        if datetime.now() < date_temp:
            date_temp = date_temp - timedelta(days = 7)
    query.date = date_temp.strftime('%Y-%m-%dT%H:%M:%S-07:00')
    query.date_is_parsed = True