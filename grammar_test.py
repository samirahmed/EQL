import nltk
import re
import sys
from termcolor import colored

def parse(parser, terminals, debug, query):
 
  debug.write(query + "\n")
  
  words = query.lower().split()
  normalized = []
  for word in words:
    if word in terminals:
      normalized.append(word)
    else:
      if len(normalized) == 0 or normalized[-1] != 'term':
        normalized.append('term')
  
  debug.write(" ".join(normalized) + "\n")
  
  parsetree = parser.parse(normalized)
  if not parsetree:
    print colored("ERROR PARSING %s " % query, 'red'),
    debug.write("PARSE ERROR \n")
  else:
    sys.stdout.write(colored('.', 'green'))
    debug.write(str(parsetree) + "\n")


lines = open("email.cfg").readlines()
grammar = '\n'.join(filter(lambda line: not line.startswith("%"),lines))
cfg = nltk.parse_cfg(grammar)
email_parser = nltk.RecursiveDescentParser(cfg)

# get a set of all terminals in the grammar
terminals = set(re.findall(r'[\"\'](.+?)[\"\']',grammar))

print colored("Terminals %s" % terminals, 'yellow')

count = 0

with  open("test.result","w") as debug: 
  for line in open('./queries.txt').readlines():
    if line and not line.startswith("#") and len(line.split()) > 0:
      parse(email_parser, terminals, debug, line)
      count += 1

print "\n%d lines parsed" % count
