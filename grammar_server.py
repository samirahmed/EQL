import nltk
import time
import re
import sys
from termcolor import colored
from bottle import route, run, template
from grammar_test import email_parser, terminals, parse, Query

debug = open("server.logs", "w")

@route('/parse/<query>')
def index(query):
  tree, wc = parse(email_parser, terminals, query, debug)
  return Query(tree , wc).json()

run(host='localhost', port=8080)
