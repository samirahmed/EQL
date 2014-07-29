import nltk
import json
import time
import re
import sys
from termcolor import colored

class Query:
  
  sender          = None
  recipients      = None
  first_text      = None
  second_text     = None
  conjunction     = None
  attachments     = None
  date            = None
  date_comparator = None
  link            = None

  index = 0

  def __init__(self, tree, wildcards):
    self._visit(tree, wildcards)
    index = 0
  
  def __str__(self):
    return str(self.properties())

  def properties(self):
    return {
     'sender': self.sender,
     'recipients': self.recipients,
     'first_text': self.first_text,
     'second_text': self.second_text,
     'conjunction': self.conjunction,
     'attachments': self.attachments,
     'link': self.link,
     'date': self.date,
     'date_comparator' : self.date_comparator
    }

  def json(self):
    return json.dumps(self.properties(), indent = 2)

  def _visit(self, tree, wildcards):
    
    if not tree or not (type(tree) == nltk.tree.Tree):
      return

    if tree.node == "TCSP":    # To Contact Specifier
      self.recipients = wildcards[self.index]
      self.index += 1

    elif tree.node == "FCSP":  # From Contact Specifier
      self.sender = wildcards[self.index]
      self.index += 1

    elif tree.node == "FTCSP": # From To Contact Specifier
      self.sender = wildcards[self.index]
      self.recipients = wildcards[self.index+1]
      self.index += 2

    elif tree.node == "TFCSP": # To From Contact Specifier 
      self.recipients = wildcards[self.index]
      self.sender = wildcards[self.index+1]
      self.index += 2

    elif tree.node == "FASP":  # Filename Attachment Specifier
      self.attachments = wildcards[self.index]
      self.index += 1

    elif tree.node == "STSP":  # Single Text Specifier
      self.first_text = wildcards[self.index]
      self.index += 1

    elif tree.node == "CTSP":  # Conjunctive Text Specifier
      self.first_text = wildcards[self.index]
      self.second_text = wildcards[self.index+1]
      self.conjunction = "and" if tree.leaves()[-2] == "and" else "or"
      self.index += 2

    elif tree.node == "LSP":   # Link Specifier
      self.link = wildcards[self.index]
      self.index += 1
    
    elif tree.node == "DSP":   # DateTime Specifier
      self.date = wildcards[self.index]
      self.date_comparator = "after" if tree.leaves()[-2] == "after" else "before"
      self.index += 1
  
    for subtree in tree:
      self._visit(subtree, wildcards)

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
    return false
  else:
    sys.stdout.write(colored(u'\u2713', 'green'))
    debug.write(str(parsetree) + "\n")
    return parsetree, wildcards

lines = open("email.cfg").readlines()
grammar = '\n'.join(filter(lambda line: not line.startswith("%"),lines))
cfg = nltk.parse_cfg(grammar)
email_parser = nltk.LeftCornerChartParser(cfg)

# get a set of all terminals in the grammar
terminals = set(re.findall(r'[\"\'](.+?)[\"\']',grammar))
count = 0

with  open("test.result","w") as debug: 
  debug.write("Terminals %s" % terminals)
  for line in open('./queries.txt').readlines():
    if line and not line.startswith("#") and len(line.split()) > 0:
      start = time.time()
      tree, wc = parse(email_parser, terminals, line, debug)
      query = Query(tree, wc)
      duration = time.time()-start
      debug.write((query).json())
      debug.write("duration %f \n" % duration)
      
      count += 1
      if count % 50 == 0:
        sys.stdout.write("\n")
      sys.stdout.flush()

print "\n%d lines parsed" % count
