import nltk
import time
import re
import sys
import os
from termcolor import colored
from bottle import route, run, template
from grammar_test import AbstractSyntaxTree, EmailQuery, email_parser, terminals

debug = open("server.logs", "w")

@route('/terminals')
def terms():
  return {'terms': list(terminals)}

@route('/debug/<query>')
def index(query):
  result = {}
  ast = AbstractSyntaxTree(email_parser, terminals, query, debug)
  eq = EmailQuery(ast)
  result["extra"] = ast.properties()
  result['result'] = eq.properties()
  return result

run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
