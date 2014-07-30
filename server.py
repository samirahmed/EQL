import sys, os, faking, grammar, query_rewriter, json
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
  return "MANGOSTEEN"

@app.route('/terminals')
def terms():
  return {'terms': list(grammar.terminals)}

@app.route('/fake')
def fake():
  return faking.fake_search()

@app.route('/query/<sentence>')
def parse(query):
  result = {}
  ast, eq = grammar.process(query, debug)
  query_rewriter.augment(eq)
  result["extra"] = ast.properties()
  result["result"] = eq.properties()
  result["emails"] = es.ElasticSearchQuery(eq).sendQuery() 
  result["result"] = { 
    "parse_success": True, 
    "duration" : 0.2, 
    "count" : len(result["emails"])
    }
  return result

@app.route('/debug/<query>')
def debug_parse(query):
  result = {}
  ast, eq = grammar.process(query, debug)
  query_rewriter.augment(eq)
  result["extra"] = ast.properties()
  result["result"] = eq.properties()
  result["emails"] = es.ElasticSearchQuery(eq).sendQuery() 
  return result

#run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
