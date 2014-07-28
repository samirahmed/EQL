import nltk
import time
import re
import sys
from termcolor import colored

def normalize(terminals, query, debug):
  
  debug.write("\n" + query)
  normalized = []
  wildcards = []

  words = query.lower().split()
  for word in words:
    if word in terminals:
      normalized.append(word)
    else:
      if len(normalized) == 0 or normalized[-1] != 'term':
        normalized.append('term')
        wildcards.append(word)
      else:
        wildcards[-1] += " " + word
  
  debug.write("NORMALIZED: " + " ".join(normalized) + "\n")
  debug.write("WILDCARDS: %s \n" % wildcards)
  return normalized, wildcards

def parse(parser, terminals, query, debug):
 
  normalized, wildcards = normalize(terminals, query, debug);
  parsetree = parser.parse(normalized)
  
  if not parsetree:
    print colored("ERROR PARSING %s " % query, 'red'),
    debug.write("PARSE ERROR \n")
  else:
    sys.stdout.write(colored(u'\u2713', 'green'))
    debug.write(str(parsetree) + "\n")

lines = open("email.cfg").readlines()
grammar = '\n'.join(filter(lambda line: not line.startswith("%"),lines))
cfg = nltk.parse_cfg(grammar)
email_parser = nltk.RecursiveDescentParser(cfg)

# get a set of all terminals in the grammar
terminals = set(re.findall(r'[\"\'](.+?)[\"\']',grammar))
count = 0

with  open("test.result","w") as debug: 
  debug.write("Terminals %s" % terminals)
  for line in open('./queries.txt').readlines():
    if line and not line.startswith("#") and len(line.split()) > 0:
      parse(email_parser, terminals, line, debug)
      count += 1
      if count % 50 == 0:
        sys.stdout.write("\n")
      sys.stdout.flush()

print "\n%d lines parsed" % count
