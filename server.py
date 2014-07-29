import nltk
import time
import re
import sys
import os
from termcolor import colored
from bottle import route, run, template
from grammar_test import AbstractSyntaxTree, EmailQuery, email_parser, terminals
from faker import Factory
from datetime import datetime

faker = Factory.create()
debug = sys.stdout

def fake_contact(times):
  global faker
  contacts = []
  for times in range(times):
    contacts.append({
      "name" : faker.first_name() + " " + faker.last_name(),
      "email" : faker.email()
    });
  return contacts

@route('/terminals')
def terms():
  return {'terms': list(terminals)}

@route('/fake')
def fake():
  global faker
  text = faker.text()
  response = {} 
  result = { "parse_success": True, "duration" : 0.2 }
  emails = []
  for times in range(len(faker.text()) % 5):
    emails.append({
    "to": fake_contact(2),
    "cc": fake_contact(4),
    "from": fake_contact(1)[0],
    "body": text,
    "subject": faker.sentence(),
    "body_preview": " ".join(text.split()[:10]),
    "has_attachment" : len(text) % 2 == 0,
    "has_links" : False,
    "sent_time" : datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    "deeplink" : "outlook://125125kj12kj124124125"
    });
  response["result"] = result
  response["emails"] = emails
  return response

@route('/debug/<query>')
def index(query):
  result = {}
  ast = AbstractSyntaxTree(email_parser, terminals, query, debug)
  eq = EmailQuery(ast)
  result["extra"] = ast.properties()
  result['result'] = eq.properties()
  return result

run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
