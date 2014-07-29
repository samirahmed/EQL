import sys, os, faking
from bottle import route, run, template, Bottle, request, response
import grammar

debug = sys.stdout
app = Bottle()

@app.hook('after_request')
def enable_cors():
  response.headers['Access-Control-Allow-Origin'] = '*'
  response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
  response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@app.route('/terminals')
def terms():
  return {'terms': list(grammar.terminals)}

@app.route('/fake')
def fake():
  return faking.fake_search()

@app.route('/debug/<query>')
def index(query):
  result = {}
  ast, eq = grammar.process(query, debug)
  result["extra"] = ast.properties()
  result['result'] = eq.properties()
  return result

run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
