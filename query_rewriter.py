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
    date_temp = None
    
    if (resp.text != "null"):
      date_temp = datetime.strptime(str(resp.text), "%Y-%m-%dT%H:%M:%S-07:00")
      
      if datetime.now().month < date_temp.month:
        date_temp = date(datetime.now().year - 1, date_temp.month, date_temp.day)
      
      elif datetime.now() < date_temp:
        date_temp -= timedelta(days = 7)
    
    return date_temp.strftime('%Y-%m-%dT%H:%M:%S-07:00')
  
  else:
    return None

def augment(query):
  if query.date:

    if not query.date_comparator:
        if query.date in days:
            query.scope = "day"
        elif query.date in months:
            query.scope = "month"
    
    date_temp = None
    
    if query.date == "this year":
        query.date = date(datetime.now().year,1,1).strftime('%Y-%m-%dT%H:%M:%S-07:00')
    
    elif query.date == "this month":
        query.date = date(datetime.now().year, datetime.now().month, 1).strftime('%Y-%m-%dT%H:%M:%S-07:00')
    
    else:
        query.date = augment_datetime(query.date)
    query.date_is_parsed = True
  
  if query.attachments:
      if query.attachments == "excel" or query.attachments == "spreadsheet":
          query.attachments = "xls xlsx"

      elif query.attachments == "word":
          query.attachments = "doc docx"

      elif query.attachments == "powerpoint" or query.attachments == "presentation":
          query.attachments = "ppt pptx"

      elif query.attachments == "image" or query.attachments == "picture":
          query.attachments = "jpg png tiff bmp"

      elif query.attachments == "video" or query.attachments == "movie":
          query.attachments = "mpeg mpg wmv"

      elif query.attachments == "audio" or query.attachments == "music":
          query.attachments = "wma"

