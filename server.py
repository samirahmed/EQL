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
  result = {}
  start = time.time()
  ast, eq = grammar.process(query, debug)
  query_rewriter.augment(eq)
  result["extra"] = ast.properties()
  result["result"] = eq.properties()
  result["emails"] = es.ElasticSearchQuery(eq).sendQuery() 
  result["result"] = { 
    "parse_success": True, 
    "duration" : time.time()-start, 
    "count" : len(result["emails"])
    }
  return result

@app.route('/parse/debug/<query>')
def debug_parse(query):
  result = {}
  ast, eq = grammar.process(query, debug)
  query_rewriter.augment(eq)
  result["extra"] = ast.properties()
  result["result"] = eq.properties()
  result["emails"] = es.ElasticSearchQuery(eq).sendQuery() 
  return result

run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
