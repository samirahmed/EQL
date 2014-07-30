import sys, os, faking, grammar, query_rewriter, json, time
import es_dictionary as es
from bottle import route, run, template, Bottle, request, response

debug = sys.stdout
app = Bottle()

def wsgi():
  return app;

@app.hook('after_request')
def enable_cors():
  response.headers['Access-Control-Allow-Origin'] = '*'
  response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
  response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@app.route('/')
def index():
  global app
  info = ""
  for route in app.routes:
    url = route.rule.replace('<','{').replace('>','}')
    info += "<code>%s %s </code><br/>" % (route.method, url)
  return info

@app.route('/terminals')
def terms():
  return {'terms': list(grammar.terminals)}

@app.route('/fake/contacts/<prefix>')
def terms(prefix):
  return { "contacts" : faking.fake_contact_resolution(prefix) }

@app.route('/parse/fake/<query>')
def fake(query):
  return faking.fake_search()

@app.route('/parse/<query>')
def parse(query):
  req_start = time.time()
  
  result = {}
  ast, eq = grammar.process(query, debug)
  
  aug_start = time.time()
  query_rewriter.augment(eq)
  aug_end = time.time()

  es_start = time.time()
  emails = es.ElasticSearchQuery(eq).sendQuery() 
  es_end = time.time()

  result["syntax"] = ast.properties()
  result["parse_terms"] = eq.parse_terms()
  result["emails"] = emails
  result["result"] = { 
    "parse_success": True, 
    "duration" : time.time()- req_start, 
    "augemtnation_duration": aug_end - aug_start,
    "query_duration" : es_end - es_start,
    "count" : len(result["emails"])
    }
  return result

run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
